"""
ATK Video AI Organizer - Local Vision-Language Model (VLM)
Generates natural language video descriptions, tags, activities, and environment context.
Supports Florence-2-base, Moondream2, and Rule-based heuristics fallback.
"""

from typing import Dict, Any, List
import cv2
from backend.models.base_model import BaseModel
from backend.utils.logger import app_logger, error_logger

class LocalVisionLanguageModel(BaseModel):
    def __init__(self, model_name: str = "florence2-base", models_dir: str = "data/models", device: str = "cpu"):
        super().__init__(model_name, models_dir, device)

    def load_model(self):
        if self.is_loaded:
            return
        try:
            from transformers import AutoProcessor, AutoModelForCausalLM
            from PIL import Image

            model_id = "microsoft/Florence-2-base"
            self._processor = AutoProcessor.from_pretrained(model_id, trust_remote_code=True, cache_dir=self.models_dir)
            self._model = AutoModelForCausalLM.from_pretrained(model_id, trust_remote_code=True, cache_dir=self.models_dir).to(self.device)
            self.is_loaded = True
            app_logger.info(f"Loaded Florence-2 VLM on {self.device}")
        except Exception as e:
            error_logger.error(f"Failed to load VLM model: {e}")
            self.is_loaded = False

    def unload_model(self):
        if self.is_loaded:
            self._model = None
            self._processor = None
            self.is_loaded = False
            app_logger.info("Unloaded VLM Model")

    def describe_frame(self, frame_bgr) -> str:
        """Runs VLM to describe a single keyframe."""
        if not self.is_loaded:
            self.load_model()

        if not self.is_loaded or self._model is None:
            return ""

        try:
            from PIL import Image
            rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(rgb)

            prompt = "<MORE_DETAILED_CAPTION>"
            inputs = self._processor(text=prompt, images=pil_img, return_tensors="pt").to(self.device)
            generated_ids = self._model.generate(
                input_ids=inputs["input_ids"],
                pixel_values=inputs["pixel_values"],
                max_new_tokens=1024,
                num_beams=3
            )
            caption = self._processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
            return caption.strip()
        except Exception as e:
            error_logger.error(f"VLM inference error: {e}")
            return ""

    def generate_video_summary(self, keyframe_samples: List[Dict[str, Any]], detected_objects: List[str], transcript_text: str, ocr_text: str) -> Dict[str, Any]:
        """
        Aggregates frame descriptions, objects, transcripts, and OCR into a unified video summary.
        """
        descriptions = []
        for sample in keyframe_samples[:3]: # Describe top 3 keyframes
            if "frame_bgr" in sample:
                desc = self.describe_frame(sample["frame_bgr"])
                if desc:
                    descriptions.append(desc)

        # Fallback description builder if VLM model is downloading or offline
        if not descriptions:
            obj_str = ", ".join(list(set(detected_objects))[:5])
            if obj_str:
                descriptions.append(f"A video featuring {obj_str}.")
            elif transcript_text:
                descriptions.append(f"A video with speech containing: '{transcript_text[:100]}...'")
            else:
                descriptions.append("A short video clip.")

        full_description = " ".join(descriptions)

        # Heuristic category & tag assignment
        tags = set(detected_objects)
        if transcript_text:
            tags.add("speech")
        if ocr_text:
            tags.add("text")

        category = "Miscellaneous"
        low_desc = (full_description + " " + " ".join(detected_objects)).lower()
        
        if any(w in low_desc for w in ["dog", "cat", "bird", "animal", "pet", "lion", "tiger", "horse"]):
            category = "Animals"
        elif any(w in low_desc for w in ["car", "motorcycle", "scooter", "bike", "vehicle", "truck", "bus", "driving", "riding"]):
            category = "Vehicles"
        elif any(w in low_desc for w in ["man", "woman", "person", "child", "people", "guy", "girl"]):
            category = "People"
        elif any(w in low_desc for w in ["phone", "laptop", "computer", "screen", "tv", "technology"]):
            category = "Technology"
        elif any(w in low_desc for w in ["food", "cooking", "eating", "dish", "meal", "kitchen"]):
            category = "Food"
        elif any(w in low_desc for w in ["game", "gaming", "playstation", "xbox", "gameplay"]):
            category = "Gaming"
        elif any(w in low_desc for w in ["meme", "funny", "whatsapp", "comedy", "laugh"]):
            category = "Memes"

        return {
            "ai_description": full_description,
            "category": category,
            "tags": list(tags)[:10]
        }

    def process(self, input_data: Any) -> Dict[str, Any]:
        """Runs VLM summary generation on keyframe samples and extracted context."""
        if isinstance(input_data, dict):
            return self.generate_video_summary(
                input_data.get("keyframe_samples", []),
                input_data.get("detected_objects", []),
                input_data.get("transcript_text", ""),
                input_data.get("ocr_text", "")
            )
        elif isinstance(input_data, list):
            return {"description": self.describe_frame(input_data[0]["frame_bgr"]) if input_data and "frame_bgr" in input_data[0] else ""}
        return {"description": self.describe_frame(input_data)}
