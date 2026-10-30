"""
Vision Transformer Grad-CAM Explainability Module
=================================================
Generates visual attention heatmaps indicating spatial patch regions
of the leaf that most influenced the ViT classification decision.
"""

from __future__ import annotations

import base64
import logging
from typing import Optional

import cv2
import numpy as np
import torch
import torch.nn.functional as F
from PIL import Image

logger = logging.getLogger(__name__)


class ViTGradCAM:
    """
    Grad-CAM implementation tailored for Vision Transformer (ViT) architectures.
    Captures post-attention layer norm activations and backpropagated gradients
    to reconstruct 14x14 spatial patch attention maps.
    """

    def __init__(self, model):
        self.model = model
        self.gradients = None
        self.activations = None

        # Hook into the final encoder layer's post-attention norm
        # Supports both transformers v4 (vit.encoder.layer) and v5 (vit.layers)
        if hasattr(self.model.vit, "encoder") and hasattr(self.model.vit.encoder, "layer"):
            target_layer = self.model.vit.encoder.layer[-1].layernorm_after
        elif hasattr(self.model.vit, "layers"):
            target_layer = self.model.vit.layers[-1].layernorm_after
        else:
            raise AttributeError("Could not locate final layernorm layer on ViT model.")

        target_layer.register_forward_hook(self._save_activations)
        target_layer.register_full_backward_hook(self._save_gradients)

    def _save_activations(self, module, input, output):
        self.activations = output

    def _save_gradients(self, module, grad_input, grad_output):
        self.gradients = grad_output[0]

    def generate_heatmap(self, pil_image: Image.Image, processor, target_class_idx: Optional[int] = None) -> str:
        """
        Generate an alpha-blended Grad-CAM attention heatmap overlay.

        Parameters
        ----------
        pil_image : PIL.Image.Image
            Input leaf image.
        processor : ViTImageProcessor
            Hugging Face ViT image preprocessor.
        target_class_idx : int, optional
            Target class index to compute gradients against. If None, uses top logit.

        Returns
        -------
        str
            Base64 encoded JPEG data URL string: 'data:image/jpeg;base64,...'
        """
        device = next(self.model.parameters()).device
        inputs = processor(images=pil_image, return_tensors="pt").to(device)

        # Ensure gradients are enabled for this pass
        self.model.zero_grad()
        outputs = self.model(**inputs)
        logits = outputs.logits

        if target_class_idx is None:
            target_class_idx = torch.argmax(logits, dim=1).item()

        # Backward pass on the target class score
        score = logits[0, target_class_idx]
        score.backward(retain_graph=True)

        if self.gradients is None or self.activations is None:
            raise RuntimeError("Gradients or activations were not captured during forward/backward pass.")

        # ViT output shape: [1, 197 tokens (1 CLS + 196 patches), 768 channels]
        # Exclude the CLS token (index 0) to keep spatial patches (1 to 196)
        grads = self.gradients[:, 1:, :]  # [1, 196, 768]
        acts = self.activations[:, 1:, :]  # [1, 196, 768]

        # Calculate channel weights via spatial token pooling
        weights = torch.mean(grads, dim=1, keepdim=True)  # [1, 1, 768]
        cam = torch.sum(weights * acts, dim=-1)  # [1, 196]
        cam = F.relu(cam)  # Only positive activations

        # Reshape the 196 patches into the original 14x14 grid
        cam = cam.view(14, 14).detach().cpu().numpy()
        cam_min, cam_max = cam.min(), cam.max()
        cam = (cam - cam_min) / (cam_max - cam_min + 1e-8)

        # Convert original PIL image to OpenCV format
        orig_np = np.array(pil_image.convert("RGB"))
        h, w, _ = orig_np.shape

        # Upscale 14x14 heatmap to original image dimensions
        heatmap_resized = cv2.resize(cam, (w, h))
        heatmap_uint8 = np.uint8(255 * heatmap_resized)

        # Apply JET colormap (Red = high attention, Blue = ignored background)
        heatmap_color = cv2.applyColorMap(heatmap_uint8, cv2.COLORMAP_JET)
        heatmap_color = cv2.cvtColor(heatmap_color, cv2.COLOR_BGR2RGB)

        # Alpha-blend the heatmap over the original leaf (60% leaf, 40% heat)
        overlay = cv2.addWeighted(orig_np, 0.6, heatmap_color, 0.4, 0)

        # Encode to Base64 JPEG for instant frontend transmission
        _, buffer = cv2.imencode(".jpg", cv2.cvtColor(overlay, cv2.COLOR_RGB2BGR))
        base64_str = base64.b64encode(buffer).decode("utf-8")
        return f"data:image/jpeg;base64,{base64_str}"
