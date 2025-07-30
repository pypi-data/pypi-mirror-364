#!/usr/bin/env python3
"""
MareArts ANPR CLI - Command Line Interface for License Plate Detection and Recognition
"""

import argparse
import json
import os
import sys
import re
import base64
import getpass
from pathlib import Path
from typing import List, Dict, Any, Optional
import configparser

try:
    import cv2
    import numpy as np
except ImportError:
    print("Error: OpenCV is required. Install with: pip install opencv-python")
    sys.exit(1)

try:
    from . import (
        marearts_anpr_from_image_file,
        marearts_anpr_from_cv2,
        marearts_anpr_from_pil,
        ma_anpr_detector,
        ma_anpr_ocr
    )
    from ._version import __version__
except ImportError:
    print("Error: MareArts ANPR is not properly installed.")
    sys.exit(1)


CONFIG_DIR = Path.home() / '.marearts'
CONFIG_FILE = CONFIG_DIR / 'anpr_config.ini'

# Environment variable names
ENV_USERNAME = 'MAREARTS_ANPR_USERNAME'
ENV_SERIAL_KEY = 'MAREARTS_ANPR_SERIAL_KEY'

# Input validation patterns
USERNAME_PATTERN = re.compile(r'^[a-zA-Z0-9_\-\.@]+$')
SERIAL_KEY_PATTERN = re.compile(r'^[A-Za-z0-9\-_=+/]+$')
ALLOWED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif'}


def ensure_config_dir():
    """Ensure configuration directory exists with proper permissions"""
    CONFIG_DIR.mkdir(mode=0o700, exist_ok=True)


def load_credentials() -> Dict[str, str]:
    """Load credentials following security priority: env vars > config file"""
    credentials = {}
    
    # Priority 1: Environment variables (most secure)
    env_username = os.getenv(ENV_USERNAME)
    env_serial_key = os.getenv(ENV_SERIAL_KEY)
    
    if env_username and env_serial_key:
        credentials = {
            'user_name': env_username,
            'serial_key': env_serial_key,
            'source': 'environment'
        }
    else:
        # Priority 2: Config file
        credentials = load_config_file()
        if credentials:
            credentials['source'] = 'config_file'
    
    return credentials


def load_config_file() -> Dict[str, str]:
    """Load configuration from file"""
    if not CONFIG_FILE.exists():
        return {}
    
    # Check file permissions for security warning
    file_stat = CONFIG_FILE.stat()
    if file_stat.st_mode & 0o077:  # Check if readable by group/others
        print(f"⚠️  Warning: {CONFIG_FILE} has insecure permissions. Run: chmod 600 {CONFIG_FILE}")
    
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)
    
    if 'credentials' not in config:
        return {}
    
    creds = dict(config['credentials'])
    # Decode the obfuscated serial key
    if 'serial_key' in creds:
        try:
            creds['serial_key'] = base64.b64decode(creds['serial_key'].encode()).decode()
        except:
            # Handle old unencoded configs
            pass
    
    return creds


def mask_serial_key(serial_key: str) -> str:
    """Mask serial key for display purposes"""
    if len(serial_key) <= 8:
        return '*' * len(serial_key)
    return serial_key[:4] + '*' * (len(serial_key) - 8) + serial_key[-4:]


def save_config(user_name: str, serial_key: str):
    """Save configuration to file with basic obfuscation"""
    ensure_config_dir()
    config = configparser.ConfigParser()
    # Basic obfuscation - not true encryption but better than plaintext
    config['credentials'] = {
        'user_name': user_name,
        'serial_key': base64.b64encode(serial_key.encode()).decode()
    }
    with open(CONFIG_FILE, 'w') as f:
        config.write(f)
    # Set restrictive permissions
    os.chmod(CONFIG_FILE, 0o600)
    print(f"Configuration saved to {CONFIG_FILE}")


def cmd_config(args):
    """Interactive configuration for license credentials"""
    print("MareArts ANPR Configuration")
    print("-" * 40)
    
    # Show credential sources and security info
    print("\nCredential Priority (most secure to least secure):")
    print(f"1. Environment variables: {ENV_USERNAME}, {ENV_SERIAL_KEY}")
    print(f"2. Configuration file: {CONFIG_FILE}")
    print("3. Interactive prompt (this command)")
    print()
    
    current_config = load_credentials()
    
    if current_config:
        source = current_config.get('source', 'unknown')
        print(f"Current configuration found (source: {source}):")
        print(f"Username: {current_config.get('user_name', 'Not set')}")
        
        serial_key = current_config.get('serial_key', '')
        if serial_key:
            print(f"Serial Key: {mask_serial_key(serial_key)}")
        else:
            print("Serial Key: Not set")
        
        if source == 'environment':
            print("\n⚠️  Note: Environment variables take priority over config file.")
            print("   To update credentials, modify environment variables or unset them.")
            if not args.force:
                response = input("Continue to update config file anyway? [y/N]: ")
                if response.lower() != 'y':
                    return
        else:
            print()
            if not args.force:
                response = input("Do you want to update the configuration? [y/N]: ")
                if response.lower() != 'y':
                    print("Configuration unchanged.")
                    return
    
    # Get username with validation
    while True:
        user_name = input("Enter username: ").strip()
        if not user_name:
            print("Username cannot be empty.")
            continue
        if not USERNAME_PATTERN.match(user_name):
            print("Invalid username format. Please use only letters, numbers, and _-.@")
            continue
        break
    
    # Get serial key with validation and masking
    while True:
        serial_key = getpass.getpass("Enter serial key: ").strip()
        if not serial_key:
            print("Serial key cannot be empty.")
            continue
        if not SERIAL_KEY_PATTERN.match(serial_key):
            print("Invalid serial key format. Please use only letters, numbers, and hyphens.")
            continue
        break
    
    save_config(user_name, serial_key)
    
    # Test the configuration
    print("\nTesting configuration...")
    try:
        detector = ma_anpr_detector('v11_middle', user_name, serial_key)
        print("✓ Configuration validated successfully!")
    except Exception:
        print("✗ Error testing configuration. Please try again.")


def cmd_gpu_info(args):
    """Display GPU/CUDA information"""
    print("MareArts ANPR GPU Information")
    print("-" * 40)
    
    # Check OpenCV build info
    build_info = cv2.getBuildInformation()
    
    # Look for CUDA info in build information
    cuda_enabled = "CUDA" in build_info and "YES" in build_info
    
    print(f"OpenCV Version: {cv2.__version__}")
    print(f"CUDA Support: {'Yes' if cuda_enabled else 'No'}")
    
    if cuda_enabled:
        # Try to get more CUDA details
        cuda_lines = [line for line in build_info.split('\n') if 'CUDA' in line]
        for line in cuda_lines[:5]:  # Show first 5 CUDA-related lines
            print(f"  {line.strip()}")
    
    # Check if GPU is available for computation
    try:
        gpu_count = cv2.cuda.getCudaEnabledDeviceCount()
        if gpu_count > 0:
            print(f"\nCUDA Devices Found: {gpu_count}")
            for i in range(gpu_count):
                cv2.cuda.setDevice(i)
                print(f"  Device {i}: Available")
        else:
            print("\nNo CUDA devices found.")
    except:
        print("\nCUDA runtime not available.")
    
    print("\nNote: MareArts ANPR will use GPU acceleration if available.")


def cmd_models(args):
    """List available models"""
    print("MareArts ANPR Available Models")
    print("=" * 50)
    
    print("\n📍 DETECTOR MODELS (12 available):")
    print("-" * 35)
    
    print("\nv10 Series:")
    v10_models = [
        ("v10_nano", "Fastest, lowest accuracy"),
        ("v10_small", "Fast, lower accuracy"),
        ("v10_middle", "Balanced performance"),
        ("v10_large", "High accuracy, slower"),
        ("v10_xlarge", "Highest accuracy, slowest")
    ]
    for model, desc in v10_models:
        print(f"  - {model:<12} {desc}")
    
    print("\nv11 Series:")
    v11_models = [
        ("v11_nano", "Fastest v11 variant"),
        ("v11_small", "Fast v11 variant"),
        ("v11_middle", "Balanced v11 variant"),
        ("v11_large", "High accuracy v11 variant")
    ]
    for model, desc in v11_models:
        print(f"  - {model:<12} {desc}")
    
    print("\nv13 Series (Latest):")
    v13_models = [
        ("v13_nano", "Fastest v13 variant"),
        ("v13_small", "Fast v13 variant"),
        ("v13_middle", "Balanced v13 variant"),
        ("v13_large", "High accuracy v13 variant")
    ]
    for model, desc in v13_models:
        print(f"  - {model:<12} {desc}")
    
    print("\n🔤 OCR MODELS (15 available):")
    print("-" * 30)
    
    print("\nBase Models:")
    base_ocr = [
        ("eu", "European license plates (40+ countries)"),
        ("kr", "Korean license plates"),
        ("euplus", "Enhanced European model"),
        ("univ", "Universal model")
    ]
    for model, desc in base_ocr:
        print(f"  - {model:<12} {desc}")
    
    print("\nv11 Series:")
    v11_ocr = [
        ("v11_eu", "v11 European model"),
        ("v11_kr", "v11 Korean model"),
        ("v11_euplus", "v11 Enhanced European model"),
        ("v11_univ", "v11 Universal model"),
        ("v11_cn", "v11 Chinese model"),
        ("v11_jp", "v11 Japanese model")
    ]
    for model, desc in v11_ocr:
        print(f"  - {model:<12} {desc}")
    
    print("\nv13 Series (Latest):")
    v13_ocr = [
        ("v13_univ", "v13 Universal model"),
        ("v13_euplus", "v13 Enhanced European model"),
        ("v13_eu", "v13 European model"),
        ("v13_kr", "v13 Korean model"),
        ("v13_cn", "v13 Chinese model")
    ]
    for model, desc in v13_ocr:
        print(f"  - {model:<12} {desc}")
    
    print(f"\n💡 RECOMMENDATIONS:")
    print("  - For best balance: v13_middle detector + v13_euplus OCR")
    print("  - For speed: v10_small detector + eu OCR") 
    print("  - For accuracy: v13_large detector + v13_univ OCR")
    print("  - Total models: 27 (12 detectors + 15 OCR models)")


def cmd_validate(args):
    """Validate license"""
    config = load_credentials()
    if not config:
        print("Error: No configuration found.")
        print(f"Set environment variables ({ENV_USERNAME}, {ENV_SERIAL_KEY}) or run 'marearts-anpr config'")
        sys.exit(1)
    
    user_name = config.get('user_name')
    serial_key = config.get('serial_key')
    source = config.get('source', 'unknown')
    
    print("Validating MareArts ANPR License")
    print("-" * 40)
    print(f"Username: {user_name}")
    print(f"Serial Key: {mask_serial_key(serial_key)}")
    print(f"Credential Source: {source}")
    
    try:
        detector = ma_anpr_detector()
        ret = detector.init(1, user_name, serial_key)
        
        if ret == 0:
            print("\n✓ License is valid and active!")
        else:
            print("\n✗ License validation failed")
            print("Please check your credentials or contact support.")
    except Exception:
        print("\n✗ Error during validation. Please try again.")


def validate_file_path(path: str) -> Optional[Path]:
    """Validate and sanitize file paths"""
    try:
        # Resolve to absolute path
        abs_path = Path(path).resolve()
        
        # Check if path exists
        if not abs_path.exists():
            return None
        
        # For files, check extension
        if abs_path.is_file():
            if abs_path.suffix.lower() not in ALLOWED_IMAGE_EXTENSIONS:
                return None
        
        return abs_path
    except Exception:
        return None


def draw_results(image: np.ndarray, results: List[Dict[str, Any]]) -> np.ndarray:
    """Draw detection results on image"""
    output = image.copy()
    
    for result in results:
        bbox = result['bbox']
        x1, y1, x2, y2 = int(bbox[0]), int(bbox[1]), int(bbox[2]), int(bbox[3])
        
        # Draw bounding box
        cv2.rectangle(output, (x1, y1), (x2, y2), (0, 255, 0), 2)
        
        # Prepare label
        ocr_text = result.get('ocr_text', 'N/A')
        ocr_conf = result.get('ocr_conf', 0.0)
        label = f"{ocr_text} ({ocr_conf:.2f})"
        
        # Draw label background
        label_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
        label_y = y1 - 10 if y1 - 10 > label_size[1] else y1 + label_size[1] + 10
        cv2.rectangle(output, 
                     (x1, label_y - label_size[1] - 5),
                     (x1 + label_size[0], label_y + 5),
                     (0, 255, 0), -1)
        
        # Draw label text
        cv2.putText(output, label,
                   (x1, label_y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
    
    return output


def process_image(image_path: str, args) -> List[Dict[str, Any]]:
    """Process single image with secure credential handling"""
    config = load_credentials()
    if not config:
        raise ValueError("No configuration found. Run 'marearts-anpr config' first.")
    
    user_name = config.get('user_name')
    serial_key = config.get('serial_key')
    
    if not user_name or not serial_key:
        raise ValueError("Invalid credentials found. Please reconfigure.")
    
    try:
        # Get model versions from args with available fallbacks
        detector_model = getattr(args, 'detector_model', 'v11_middle')  # Fallback to available model
        ocr_model = getattr(args, 'ocr_model', 'euplus')  # Fallback to available model
        
        # Create detector object with correct parameters
        detector = ma_anpr_detector(detector_model, user_name, serial_key)
        
        # Create OCR object with correct parameters  
        ocr = ma_anpr_ocr(ocr_model, user_name, serial_key)
        
        # Use the correct API with initialized objects
        api_result = marearts_anpr_from_image_file(detector, ocr, image_path)
        
        # Convert API format to expected CLI format
        if api_result and 'results' in api_result:
            results = []
            for result in api_result['results']:
                # Convert to expected format
                plate_result = {
                    'ocr_text': result.get('ocr', ''),
                    'ocr_conf': result.get('ocr_conf', 0) / 100.0 if result.get('ocr_conf', 0) > 1 else result.get('ocr_conf', 0),  # Convert percentage to decimal
                    'bbox': result.get('ltrb', []),
                    'bbox_conf': result.get('ltrb_conf', 0) / 100.0 if result.get('ltrb_conf', 0) > 1 else result.get('ltrb_conf', 0)
                }
                results.append(plate_result)
            return results
        else:
            return []
        
    except Exception as e:
        # Generic error message to avoid credential leakage
        raise ValueError("Failed to process image. Please check your configuration and license.")
    finally:
        # Clear sensitive variables from memory
        user_name = None
        serial_key = None


def cmd_read(args):
    """Read license plates from images"""
    # Check configuration
    config = load_credentials()
    if not config:
        print("Error: No configuration found.")
        print(f"Set environment variables ({ENV_USERNAME}, {ENV_SERIAL_KEY}) or run 'marearts-anpr config'")
        sys.exit(1)
    
    # Get list of input files with validation
    input_files = []
    for input_path in args.input:
        path = validate_file_path(input_path)
        if path is None:
            print(f"Warning: {input_path} is not a valid image file or directory, skipping.")
            continue
            
        if path.is_file():
            input_files.append(path)
        elif path.is_dir():
            # Find all image files in directory
            for ext in ALLOWED_IMAGE_EXTENSIONS:
                input_files.extend(path.glob(f'*{ext}'))
                input_files.extend(path.glob(f'*{ext.upper()}'))
    
    if not input_files:
        print("Error: No valid input files found.")
        sys.exit(1)
    
    print(f"Processing {len(input_files)} image(s)...")
    print(f"Detector model: {args.detector_model}")
    print(f"OCR model: {args.ocr_model}")
    print(f"Confidence threshold: {args.confidence}")
    print("-" * 40)
    
    all_results = []
    
    for img_path in input_files:
        try:
            print(f"\nProcessing: {img_path}")
            
            # Process image
            results = process_image(str(img_path), args)
            
            # Filter by confidence
            filtered_results = [r for r in results if r.get('ocr_conf', 0) >= args.confidence]
            
            # Store results with filename
            for result in filtered_results:
                result['filename'] = str(img_path)
            
            all_results.extend(filtered_results)
            
            # Display results
            if filtered_results:
                print(f"  Found {len(filtered_results)} plate(s):")
                for i, result in enumerate(filtered_results):
                    print(f"    {i+1}. {result.get('ocr_text', 'N/A')} (confidence: {result.get('ocr_conf', 0):.3f})")
            else:
                print("  No plates detected above confidence threshold.")
            
            # Save annotated image if requested
            if args.output:
                image = cv2.imread(str(img_path))
                annotated = draw_results(image, filtered_results)
                
                if len(input_files) == 1:
                    output_path = args.output
                else:
                    # Multiple files - create unique output names
                    output_path = Path(args.output)
                    if output_path.is_dir():
                        output_path = output_path / f"detected_{img_path.name}"
                    else:
                        output_path = output_path.parent / f"detected_{img_path.stem}{output_path.suffix}"
                
                cv2.imwrite(str(output_path), annotated)
                print(f"  Saved annotated image: {output_path}")
                
        except Exception as e:
            # Show more specific error information for debugging
            print(f"  Error: Failed to process image - {str(e)}")
            continue
    
    # Save results to JSON if requested
    if args.json:
        try:
            json_path = Path(args.json).resolve()
            with open(json_path, 'w') as f:
                json.dump(all_results, f, indent=2)
            print(f"\nResults saved to: {json_path}")
        except Exception:
            print("\nError: Failed to save JSON results")
    
    # Summary
    print(f"\nSummary: Detected {len(all_results)} plate(s) from {len(input_files)} image(s)")


def cmd_version(args):
    """Show version information"""
    print(f"MareArts ANPR CLI v{__version__}")


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        prog='marearts-anpr',
        description='MareArts ANPR CLI - License Plate Detection and Recognition'
    )
    
    # Add direct file support - if first arg looks like a file, treat as read command
    if len(sys.argv) > 1 and not sys.argv[1].startswith('-') and sys.argv[1] not in ['config', 'gpu-info', 'models', 'validate', 'read', 'version']:
        # Check if it could be a file path, glob pattern, or directory
        potential_file = sys.argv[1]
        # Accept any path-like argument (files, directories, glob patterns)
        if '.' in potential_file or '/' in potential_file or '\\' in potential_file or '*' in potential_file or Path(potential_file).exists():
            # Insert 'read' command
            sys.argv.insert(1, 'read')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Config command
    config_parser = subparsers.add_parser('config', help='Configure license credentials')
    config_parser.add_argument('--force', action='store_true', help='Force reconfiguration')
    
    # GPU info command
    gpu_parser = subparsers.add_parser('gpu-info', help='Display GPU/CUDA information')
    
    # Models command
    models_parser = subparsers.add_parser('models', help='List available models')
    
    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate license')
    
    # Version command
    version_parser = subparsers.add_parser('version', help='Show version information')
    
    # Read command
    read_parser = subparsers.add_parser('read', help='Read license plates from images')
    read_parser.add_argument('input', nargs='+', help='Input image file(s) or directory')
    read_parser.add_argument('--detector-model', default='v13_middle',
                              choices=['v10_nano', 'v10_small', 'v10_middle', 'v10_large', 'v10_xlarge',
                                       'v11_nano', 'v11_small', 'v11_middle', 'v11_large',
                                       'v13_nano', 'v13_small', 'v13_middle', 'v13_large'],
                              help='Detector model version (default: v13_middle)')
    read_parser.add_argument('--ocr-model', default='v13_euplus',
                              choices=['eu', 'kr', 'euplus', 'univ',
                                       'v11_eu', 'v11_kr', 'v11_euplus', 'v11_univ', 'v11_cn', 'v11_jp',
                                       'v13_univ', 'v13_euplus', 'v13_eu', 'v13_kr', 'v13_cn'],
                              help='OCR model version (default: v13_euplus)')
    read_parser.add_argument('--confidence', type=float, default=0.5,
                              help='Minimum confidence threshold (default: 0.5)')
    read_parser.add_argument('--output', help='Output path for annotated image(s)')
    read_parser.add_argument('--json', help='Save results to JSON file')
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Execute command
    try:
        if args.command == 'config':
            cmd_config(args)
        elif args.command == 'gpu-info':
            cmd_gpu_info(args)
        elif args.command == 'models':
            cmd_models(args)
        elif args.command == 'validate':
            cmd_validate(args)
        elif args.command == 'version':
            cmd_version(args)
        elif args.command == 'read':
            # Set defaults for direct invocation if not set
            if not hasattr(args, 'detector_model'):
                args.detector_model = 'v13_middle'
            if not hasattr(args, 'ocr_model'):
                args.ocr_model = 'v13_euplus'
            if not hasattr(args, 'confidence'):
                args.confidence = 0.5
            if not hasattr(args, 'output'):
                args.output = None
            if not hasattr(args, 'json'):
                args.json = None
            cmd_read(args)
    except KeyboardInterrupt:
        print("\nOperation cancelled.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()