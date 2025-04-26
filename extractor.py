import os
import re
from pdfminer.high_level import extract_text



class Extractor():
    def __init__(self):
        pass

    def convert_pdf_to_raw_text(self, file):
        raw_text = extract_text(file)
        return raw_text

    def clean_text(self, text):
        text = re.sub(r'\n\s*\n', '\n', text)
        text = re.sub(r' {2,}', ' ', text)
        text = text.lower()
        return text

    def remove_line_breaks(self, text):
        if None is text:
            return None
        return re.sub(r'\n', ' ', text)


    def general_extract(self, text, start_boundary, end_boundary, max_length=None, inclusive_return=False):
        if text is None:
            return None
        if max_length:
            # Use a quantifier that allows up to max_length characters.
            middle_pattern = rf'(.{{0,{max_length}}})'
        else:
            # Fall back to lazy matching if no max_length is provided.
            middle_pattern = r'(.*?)'

        pattern = rf'({"|".join(map(re.escape, start_boundary))}){middle_pattern}({"|".join(map(re.escape, end_boundary))})'

        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if match:
            # Use group(0) if inclusive_return, otherwise group(2) which is the captured text in between.
            extracted_data = match.group().strip() if inclusive_return else match.group(2).strip()
            if max_length and len(extracted_data) > max_length:
                return None
            return extracted_data
        return None


    def extract_title(self, text, max_length=None):
        start_boundary = ['a.c.', 'a. c.', 'a c', 'a. c', 'a.c']
        end_boundary = ['__', 'por\n', 'por \n', 'por:\n', 'por: \n']
        return self.general_extract(text, start_boundary, end_boundary, max_length)

    def extract_author(self, text, max_length=None):
        start_boundary = ['por\n', 'por \n', 'por:\n', 'por: \n']
        end_boundary = ['\n']
        return self.general_extract(text, start_boundary, end_boundary, max_length)

    def extract_programa(self, text, max_length=None):
        start_boundary = ['grado de\n', 'grado de \n', 'grado de:\n', 'grado de: \n', 'grado de ', 'grado de:']
        end_boundary = ['\n']
        return self.general_extract(text, start_boundary, end_boundary, max_length)

    def extract_fecha(self, text, max_length=None):
        start_boundary = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
        end_boundary = [str(year) for year in range(1960, 2050)]
        return self.general_extract(text, start_boundary, end_boundary, max_length, inclusive_return = True)

    def extract_coordinacion(self, text, max_length=None):
        start_boundary = ['coordinacion de ','coordinación de ','aprobada por la\n', 'aprobada por la \n', 'aprobada por la:\n', 'aprobada por la: \n',
                      'aprobada por:\n', 'aprobada por\n', 'aprobada por: \n', 'aprobada por \n']
        end_boundary = ['como requisito', 'como ']
        return self.general_extract(text, start_boundary, end_boundary, max_length)

    def extract_sede(self, text, max_length=None):
        start_boundary = [
            "guaymas,", "culiacán,", "mazatlán,", "cuauhtémoc,", "delicias,", "tepic,", "pachuca,", "hermosillo,",
            "guaymas ", "culiacán ", "mazatlán ", "cuauhtémoc ", "delicias ", "tepic ", "pachuca ", "hermosillo "
        ]
        end_boundary = ["sonora", "sinaloa", "chihuahua", "nayarit", "hidalgo"]
        return self.general_extract(text, start_boundary, end_boundary, max_length, inclusive_return = True)


    def extract_resumen(self, text, max_length=None):
        start_boundary = ['resumen\n', 'resumen \n']
        end_boundary = ['palabras clave', 'palabras  clave']
        return self.general_extract(text, start_boundary, end_boundary, max_length)

    def extract_abstract(self, text, max_length=None):
        start_boundary = ['abstract\n', 'abstract \n']
        end_boundary = ['\nkeywords', 'keywords:', 'keywords :', 'keywords.', 'key words:', 'key words :']
        return self.general_extract(text, start_boundary, end_boundary, max_length)

    def extract_palabras_clave(self, text, max_length=None):
        start_boundary = ['palabras clave:', 'palabras clave :', 'palabras claves:', 'palabras claves :', 'palabras clave']
        end_boundary = ['abstract']
        return self.general_extract(text, start_boundary, end_boundary, max_length)
    
    def extract_comite(self, text, max_length=None):
        start_boundary = ['miembros del comite', 'miembros del comité']
        end_boundary = ['\f']
        comite_raw = self.remove_line_breaks(self.general_extract(text, start_boundary, end_boundary, max_length))
        if comite_raw is None:
            return []
        comite = []
        start_boundary_2  = ['_']
        end_boundary_2 =  ['tesis']
        while True:
            result = self.general_extract(comite_raw, start_boundary_2, end_boundary_2, max_length=None, inclusive_return=True)
            if result is None:
                break
            end_position = comite_raw.find(result) + len(result)
            comite.append(result.replace("_",""))
            comite_raw = comite_raw[end_position:]
        return comite

    
    def extract_all_fields(self, text):
        return {
            "titulo": self.remove_line_breaks(self.extract_title(text)),
            "autor": self.remove_line_breaks(self.extract_author(text)),
            "programa": self.remove_line_breaks(self.extract_programa(text)),
            "fecha": self.remove_line_breaks(self.extract_fecha(text)),
            "coordinacion": self.remove_line_breaks(self.extract_coordinacion(text)),
            "comite": self.extract_comite(text),
            "resumen": self.remove_line_breaks(self.extract_resumen(text)),
            "abstract": self.remove_line_breaks(self.extract_abstract(text)),
            "palabras_clave": self.remove_line_breaks(self.extract_palabras_clave(text))
        }

    def get_fields_from_pdf(self, file):
        raw_text = self.convert_pdf_to_raw_text(file)
        if not raw_text or raw_text.strip() == '':
            return None
        text = self.clean_text(raw_text)
        return self.extract_all_fields(text)
