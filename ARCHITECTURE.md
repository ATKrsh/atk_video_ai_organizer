# ATK Video AI Organizer — System Architecture & Design

## Hardware-Aware AI Pipeline (RTX 3050 Optimized)

```
+-----------------------------------------------------------------------+
|                            USER INTERFACE                             |
|    PySide6 Modern Dark UI (Dashboard, Import, Library, Search, etc.)  |
+-----------------------------------┬-----------------------------------+
                                    |
+-----------------------------------▼-----------------------------------+
|                        DATABASE & VECTOR INDEX                        |
|    SQLite Database (WAL Mode)  +  FAISS Vector Index (IndexFlatIP)   |
+-----------------------------------┬-----------------------------------+
                                    |
+-----------------------------------▼-----------------------------------+
|                     INTERRUPTIBLE PIPELINE QUEUE                      |
|                                                                       |
|  1. Metadata Extractor ---> 2. Scene Detector & Keyframe Sampler      |
|  3. Quality Analyzer  ---> 4. YOLOv8 Object Detector                  |
|  5. EasyOCR Engine    ---> 6. faster-whisper Speech Transcriber     |
|  7. Florence-2 VLM    ---> 8. CLIP Vector Embedding Generator        |
+-----------------------------------------------------------------------+
```

## VRAM Management Strategy

To ensure optimal performance on an NVIDIA RTX 3050 (8 GB VRAM):
1. **Dynamic VRAM Budgeting**: Models are loaded and evaluated sequentially or offloaded if VRAM exceeds 5.5 GB.
2. **Staged Inference**:
   - YOLO runs fast frame detection on GPU (< 0.5 GB VRAM)
   - Whisper runs speech transcription on GPU with float16 compute (< 1.5 GB VRAM)
   - Florence-2 / Moondream VLM runs on keyframes (< 2.5 GB VRAM)
   - Vector Embedding runs sentence encoding (< 0.3 GB VRAM)
3. **CPU Fallback**: If CUDA is unavailable, the pipeline smoothly transitions to CPU execution.
