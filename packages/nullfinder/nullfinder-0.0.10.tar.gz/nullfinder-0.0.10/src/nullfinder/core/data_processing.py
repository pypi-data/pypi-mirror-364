import gzip
import logging
from dataclasses import dataclass
from typing import Optional
from xml.etree import ElementTree as ET

import pandas as pd

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


@dataclass
class ProcessedGameData:
    xml_tree_snippet: ET.Element
    dataframe: pd.DataFrame


def load_and_process_savegame(
    file_path: str,
) -> Optional[ProcessedGameData]:
    try:
        with gzip.open(file_path, "rb") as f:
            xml_content = f.read().decode("utf-8")
            xml_root = ET.fromstring(xml_content)

            return _extract_trade_data_from_xml(xml_root)

    except FileNotFoundError:
        logging.error(f"File not found: {file_path}")
        return None
    except gzip.BadGzipFile:
        logging.error(f"File is not a valid gzip file: {file_path}")
        return None
    except ET.ParseError as e:
        logging.error(f"Error parsing XML file {file_path}: {e}")
        return None
    except Exception as e:
        logging.error(f"An unexpected error occurred while processing {file_path}: {e}")
        return None


def _extract_trade_data_from_xml(root: ET.Element) -> ProcessedGameData:
    data = []
    trade_entries_root = ET.Element("trades")

    for entry in root.findall(".//entries[@type='trade']"):
        for log in entry.findall(".//log"):
            trade_entries_root.append(log)
            data.append(log.attrib)

    df = pd.DataFrame(data)

    return ProcessedGameData(xml_tree_snippet=trade_entries_root, dataframe=df)
