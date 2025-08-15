"""Plain text resume parser implementation."""

import logging

logger = logging.getLogger(__name__)


class TextParser:
    """Parser for plain text resume files."""
    
    def extract_text(self, file_path: str) -> str:
        """
        Extract text from a plain text file.
        
        Args:
            file_path: Path to the text file
            
        Returns:
            Extracted text as a string
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except UnicodeDecodeError:
            # Try different encodings if UTF-8 fails
            encodings = ['latin-1', 'cp1252', 'iso-8859-1']
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as file:
                        logger.info(f"Successfully read file with {encoding} encoding")
                        return file.read()
                except UnicodeDecodeError:
                    continue
            
            raise UnicodeDecodeError(
                f"Unable to decode file {file_path} with any common encoding"
            )