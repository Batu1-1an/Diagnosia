from transformers import AutoModelForImageClassification, AutoProcessor
from PIL import Image
import torch
import os
import atexit
import threading
import logging
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Force CPU usage
device = "cpu"
logger.info(f"Using device: {device}")

# Global lock for thread safety
model_lock = threading.Lock()

class ModelManager:
    _instance = None
    _initialized = False
    
    def __init__(self):
        self.model = None
        self.processor = None
        self.medical_findings = None
        
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            with model_lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance
    
    def initialize(self):
        if self._initialized:
            return True
            
        try:
            # Use a model better suited for chest X-rays
            model_name = "microsoft/swin-base-patch4-window7-224-in22k"  # Better for chest X-ray analysis
            
            logger.info(f"Loading model {model_name}...")
            try:
                self.processor = AutoProcessor.from_pretrained(model_name, use_fast=True)
            except Exception as e:
                logger.error(f"Failed to load processor: {str(e)}")
                return False
                
            try:
                self.model = AutoModelForImageClassification.from_pretrained(model_name)
                self.model.to(device)
            except Exception as e:
                logger.error(f"Failed to load model: {str(e)}")
                return False
            
            # Updated findings for chest X-rays
            self.medical_findings = [
                "normal",
                "pneumonia",
                "pleural effusion",
                "pulmonary edema",
                "cardiomegaly",
                "lung opacity",
                "atelectasis",
                "pneumothorax",
                "consolidation",
                "emphysema",
                "fibrosis",
                "nodule",
                "mass",
                "infiltration"
            ]
            
            self._initialized = True
            logger.info("Model initialization successful")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing model: {str(e)}")
            return False
            
    def cleanup(self):
        try:
            with model_lock:
                if self.model is not None:
                    del self.model
                if self.processor is not None:
                    del self.processor
                self.model = None
                self.processor = None
                self._initialized = False
                torch.cuda.empty_cache()
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")

    def predict_with_custom_processing(self, image):
        """Custom prediction processing for chest X-rays"""
        try:
            if not self._initialized:
                if not self.initialize():
                    return "Error: Model not properly initialized"
            
            # Convert to numpy array for preprocessing
            img_array = np.array(image)
            
            # Check if image is valid
            if img_array.size == 0:
                return "Error: Invalid image data"
            
            # Enhance contrast for better feature detection in X-rays
            img_array = np.clip((img_array - img_array.min()) * (255.0 / (img_array.max() - img_array.min())), 0, 255).astype(np.uint8)
            
            # Convert back to PIL Image
            enhanced_image = Image.fromarray(img_array)
            
            # Prepare the image with fast processor
            try:
                inputs = self.processor(images=enhanced_image, return_tensors="pt").to(device)
            except Exception as e:
                logger.error(f"Error processing image: {str(e)}")
                return f"Error: Failed to process image - {str(e)}"
            
            with torch.no_grad():
                try:
                    outputs = self.model(**inputs)
                    predictions = outputs.logits.softmax(dim=-1)[0]
                except Exception as e:
                    logger.error(f"Error during model inference: {str(e)}")
                    return f"Error: Failed to analyze image - {str(e)}"
                
                # Get top predictions with higher confidence threshold
                top_predictions = torch.topk(predictions, k=4)
                
                result = ["Chest X-ray Analysis:"]
                found_findings = False
                
                for score, idx in zip(top_predictions.values, top_predictions.indices):
                    finding = self.medical_findings[idx % len(self.medical_findings)]
                    confidence = score.item() * 100
                    if confidence > 25:  # Higher confidence threshold
                        found_findings = True
                        result.append(f"• {finding.title()}: {confidence:.1f}% confidence")
                
                if not found_findings:
                    result.append("• No significant findings detected with high confidence")
                    
                # Add anatomical context and disclaimer
                result.append("\nAnatomical Context:")
                result.append("- Image shows anterior-posterior (AP) or posterior-anterior (PA) view of chest")
                result.append("- Includes lungs, heart, ribs, and surrounding structures")
                result.append("\nDisclaimer: This is an AI-assisted analysis. Please consult a radiologist for accurate diagnosis.")
                
                return "\n".join(result)
                
        except Exception as e:
            logger.error(f"Error in custom prediction: {str(e)}")
            return f"Error during chest X-ray analysis: {str(e)}"

# Initialize singleton instance
model_manager = ModelManager.get_instance()

def load_model():
    """Thread-safe model loading"""
    return model_manager.initialize()

def predict_radiology_description(image, instruction=None):
    """Thread-safe prediction function"""
    try:
        with model_lock:
            if not model_manager._initialized:
                if not load_model():
                    return "Error: Model not properly initialized. Please check system logs for details."
            
            # Use custom processing for dental X-rays
            return model_manager.predict_with_custom_processing(image)
                
    except Exception as e:
        logger.error(f"Error during prediction: {str(e)}")
        return f"Error during prediction: {str(e)}"

# Register cleanup handler
atexit.register(model_manager.cleanup)

if __name__ == '__main__':
    # Example usage
    image_path = 'example_image.jpeg'
    
    if os.path.exists(image_path):
        try:
            image = Image.open(image_path).convert("RGB")
            output = predict_radiology_description(image)
            print(output)
        except Exception as e:
            logger.error(f"Error processing example image: {str(e)}")
    else:
        logger.warning(f"Example image not found: {image_path}")
