"""
Reusable helper for saving a single upload (PDF, PPTX, DOCX) / a ZIP / multiple file uploads at 
once—with a mix of PDF, PPTX, DOCX, and ZIPs containing only permitted formats.

Core upload handler  
----------
handle_uploaded_file(file_obj: List[FileStorage], target_dir: Path) -> Dict[str, List[Dict[str, str]]]
     Process a list of file uploads (PDF, PPTX, DOCX, or ZIPs containing them).  
     Return a dictionary with "success" and "error" lists of messages.

Logging
-------
A console sink and a daily-rotating JSON file sink are configured automatically on import.
"""

from __future__ import annotations

import sys
import zipfile
from pathlib import Path
from typing import Dict, Tuple, List

from loguru import logger
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

# --------------------------------------------------------------------------- #
# Loguru – console + rotating JSON file                                       #
# --------------------------------------------------------------------------- #
logger.remove()  # replace default sink

LOG_DIR = Path("upload_logs")
LOG_DIR.mkdir(exist_ok=True)

logger.add(LOG_DIR / "app_{time:YYYYMMDD}.log",
           rotation="00:00",         # New file is created daily at midnight
           retention="7 days",       # Keep logs for 10 days
           compression="zip",        # Compress logs older than 10 days
           level="DEBUG",            # Capture everything from DEBUG level
           backtrace=True,           # Capture full tracebacks on errors
           diagnose=True,
           enqueue=True,)            # Show detailed information about variables
           
logger.add(sys.stdout, 
           level="INFO",
           enqueue=True,# Console logs are less verbose (INFO level)
           format="<green>{time}</green> <level>{level}</level> <cyan>{message}</cyan>")

# --------------------------------------------------------------------------- #
# Constants                                                                   #
# --------------------------------------------------------------------------- #
ALLOWED_FILE_EXTENSIONS = {"pdf", "pptx", "docx", "xlsx"}        
ALLOWED_EXTENSIONS = ALLOWED_FILE_EXTENSIONS | {"zip"}     # HTTP-level
ALLOWED_ZIP_CONTENT_EXTENSIONS = ALLOWED_FILE_EXTENSIONS   # inside ZIP


# --------------------------------------------------------------------------- #
# Helper functions                                                            #
# --------------------------------------------------------------------------- #
def allowed_file(filename: str, allowed_exts=ALLOWED_EXTENSIONS) -> bool:
    """
    Check if **filename** ends with an extension in *allowed_exts*.

    Parameters
    ----------
    filename : str
        Name sent by the client.
    allowed_exts : set[str]
        Lower-case extensions **without** a leading dot.
    """
    result = "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_exts
    logger.debug(f"allowed_file('{filename}') → {result}")
    return result

def is_valid_zip(zip_path: Path, allowed_inside_exts=ALLOWED_ZIP_CONTENT_EXTENSIONS) -> Tuple[bool, str | None]:
    """
    Validate that **zip_path** contains at least one file with allowed extension.

    Returns
    -------
    (is_valid, warning)
        *is_valid* is True if at least one allowed file exists.
        *warning* contains info about disallowed files if any (not an error).
    """
    try:
        with zipfile.ZipFile(zip_path) as archive:
            valid_found = False
            disallowed_files = []

            for member in archive.infolist():
                if member.is_dir():
                    continue
                ext = Path(member.filename).suffix.lower().lstrip(".")
                if ext in allowed_inside_exts:
                    valid_found = True
                else:
                    disallowed_files.append(member.filename)

            if not valid_found:
                logger.warning(f"No valid files found in ZIP '{zip_path.name}'")
                return False, "No valid files found in ZIP"

            if disallowed_files:
                logger.warning(f"ZIP '{zip_path.name}' contains disallowed files: {disallowed_files}")
                return True, f"Ignored unsupported files: {', '.join(disallowed_files)}"

            return True, None

    except zipfile.BadZipFile:
        logger.error(f"Corrupted or invalid ZIP file: {zip_path}")
        return False, "Corrupted or invalid ZIP file"
    except Exception as e:
        logger.exception("Unexpected error while validating ZIP")
        return False, str(e)

def extract_zip(zip_path: Path, target_dir: Path) -> None:
    """Extract **zip_path** into **target_dir** and remove the archive."""
    try:
        with zipfile.ZipFile(zip_path) as archive:
            archive.extractall(target_dir)
        logger.info(f"ZIP extracted to {target_dir}")
    except Exception as exc:  
        logger.exception("ZIP extraction failed")
        raise RuntimeError("Failed to extract ZIP file.") from exc
    finally:
        zip_path.unlink(missing_ok=True)  # always delete archive

# --------------------------------------------------------------------------- #
# Core upload handler                                                                   #
# --------------------------------------------------------------------------- #

def handle_uploaded_file(file_objs: List[FileStorage], target_dir: Path) -> Dict[str, List[Dict[str, str]]]:
    """
    Process a list of file uploads (PDF, PPTX, DOCX, or ZIPs containing them).

    Parameters
    ----------
    file_obj : List[werkzeug.datastructures.FileStorage]
        Incoming list of files from `request.files.getlist("files")`.
    target_dir : pathlib.Path
        Destination directory (created if absent).

    Returns
    -------
    dict
       A dictionary with "success" and "error" lists of messages.
    """
    results = {"success": [], "error": []}
    target_dir.mkdir(parents=True, exist_ok=True)
    
    for file_obj in file_objs:
        filename = secure_filename(file_obj.filename or "")
        if not filename:
            logger.warning("Empty filename encountered.")
            results["error"].append({"filename": None, "message": "File name cannot be empty."})
            continue
        if not allowed_file(filename):
            logger.warning(f"Unsupported file extension: {filename}")
            results["error"].append({
                "filename": filename,
                "message": f"Allowed types: {', '.join(sorted(ALLOWED_EXTENSIONS))}."
            })
            continue
        file_path = target_dir / filename
        try:
            file_obj.save(file_path)
            logger.info(f"Upload saved to {file_path}")
        except Exception:
            logger.exception("Failed to save uploaded file")
            results["error"].append({
                "filename": filename,
                "message": "Could not save the uploaded file."
            })
            continue
            
        # Handle ZIPs
        if file_path.suffix.lower() == ".zip":
            is_valid, offending = is_valid_zip(file_path)
            if not is_valid:
                file_path.unlink(missing_ok=True)
                logger.error(f"ZIP validation failed for {filename}")
                results["error"].append({
                    "filename": filename,
                    "message": f"ZIP contains unsupported file: {offending}"
                })
                continue
            try:
                extract_zip(file_path, target_dir)
                results["success"].append({"filename": filename, "message": "ZIP extracted successfully."})
            except RuntimeError as exc:
                results["error"].append({"filename": filename, "message": str(exc)})

        else:
            results["success"].append({"filename": filename, "message": f"{filename} uploaded successfully."})

    return results
