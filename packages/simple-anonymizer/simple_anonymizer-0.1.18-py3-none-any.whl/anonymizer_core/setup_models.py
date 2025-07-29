"""Setup script to ensure spaCy models are properly installed."""

import subprocess
import sys
import os
import ssl
import urllib.request
from typing import Optional


def install_spacy_model(model_name: str = "en_core_web_lg") -> bool:
    """Install spaCy model if not already available."""
    try:
        import spacy

        # Check if model is already installed
        if spacy.util.is_package(model_name):
            print(f"✅ spaCy model '{model_name}' is already installed")
            return True

        print(f"📥 Installing spaCy model '{model_name}'...")

        # Try direct wheel installation first (best for corporate networks)
        wheel_urls = {
            "en_core_web_lg": "https://github.com/explosion/spacy-models/releases/download/en_core_web_lg-3.8.0/en_core_web_lg-3.8.0-py3-none-any.whl",
            "en_core_web_md": "https://github.com/explosion/spacy-models/releases/download/en_core_web_md-3.8.0/en_core_web_md-3.8.0-py3-none-any.whl",
            "en_core_web_sm": "https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.8.0/en_core_web_sm-3.8.0-py3-none-any.whl"
        }

        if model_name in wheel_urls:
            try:
                # First try with SSL verification enabled
                result = subprocess.run([
                    sys.executable, "-m", "pip", "install", wheel_urls[model_name]
                ], capture_output=True, text=True, check=True)
                print(f"✅ Successfully installed {model_name} via pip")
                return True
            except subprocess.CalledProcessError as e:
                print(f"⚠️ Failed to install {model_name} with SSL verification: {e.stderr}")

                # Try with trusted hosts for corporate networks
                try:
                    print("🔄 Trying with trusted hosts configuration...")
                    result = subprocess.run([
                        sys.executable, "-m", "pip", "install",
                        "--trusted-host", "github.com",
                        "--trusted-host", "objects.githubusercontent.com",
                        "--trusted-host", "pypi.org",
                        "--trusted-host", "pypi.python.org",
                        "--trusted-host", "files.pythonhosted.org",
                        wheel_urls[model_name]
                    ], capture_output=True, text=True, check=True)
                    print(f"✅ Successfully installed {model_name} via pip with trusted hosts")
                    return True
                except subprocess.CalledProcessError as e2:
                    print(f"❌ Final attempt failed for {model_name}: {e2.stderr}")
                    print(f"   You may need to manually install or configure SSL certificates")
                    return False
        else:
            print(f"❌ No wheel URL available for model: {model_name}")
            return False

    except ImportError:
        print("❌ spaCy is not installed. Please install spaCy first.")
        return False
    except Exception as e:
        print(f"❌ Unexpected error installing {model_name}: {e}")
        return False


def setup_models() -> None:
    """Setup all required spaCy models."""
    print("🔧 Setting up spaCy models for simple-anonymizer...")

    # Install the default model (large for best accuracy)
    success_large = install_spacy_model("en_core_web_lg")

    # Also install the small model for text-anonymizer compatibility
    print("\n📥 Installing en_core_web_sm for text-anonymizer compatibility...")
    success_small = install_spacy_model("en_core_web_sm")

    if success_large:
        print("✅ Primary spaCy model (en_core_web_lg) setup completed successfully!")
    else:
        print("⚠️  Primary spaCy model setup failed. You may need to install manually:")
        print("   pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_lg-3.8.0/en_core_web_lg-3.8.0-py3-none-any.whl")

    if success_small:
        print("✅ text-anonymizer compatibility model (en_core_web_sm) setup completed!")
    else:
        print("⚠️  text-anonymizer model setup failed. Install manually:")
        print("   pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.8.0/en_core_web_sm-3.8.0-py3-none-any.whl")


if __name__ == "__main__":
    setup_models()
