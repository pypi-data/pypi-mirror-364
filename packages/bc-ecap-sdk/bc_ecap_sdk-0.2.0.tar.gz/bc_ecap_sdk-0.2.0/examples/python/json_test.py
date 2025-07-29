import json
import base64
import logging
from logger import getLogger
logger = getLogger(logging.INFO)


class EEGData:
    @staticmethod
    def from_json(json, lead_off_chip):
        timestamp = json["timestamp"]
        data = json["data"]
        return EEGData(timestamp, lead_off_chip, base64.b64decode(data))

    def __init__(self, timestamp, lead_off_chip, channel_values):
        self.timestamp = timestamp
        self.lead_off_chip = lead_off_chip
        self.channel_values = channel_values

    def __repr__(self):
        return f"eeg timestamp={self.timestamp}, len={len(self.channel_values)}"
        # return f"EEGData(timestamp={self.timestamp}, channel_values={list(self.channel_values)})"


class EEGMessage:
    @staticmethod
    def from_json(json_data):
        msgId = json_data["msgId"]
        eeg_samples = []
        if "eeg" in json_data and json_data["eeg"] is not None:
            eeg = json_data["eeg"]
            if eeg and "data" in eeg and eeg["data"]:
                lead_off_chip = "CHIP_UNKNOWN"
                if "leadOffChip" in eeg:
                    lead_off_chip = eeg["leadOffChip"]
                if "sample1" in eeg["data"]:
                    sample1 = EEGData.from_json(eeg["data"]["sample1"], lead_off_chip)
                    # print(sample1)
                    eeg_samples.append(sample1)
                if "sample2" in eeg["data"]:
                    sample2 = EEGData.from_json(eeg["data"]["sample2"], lead_off_chip)
                    # print(sample2)
                    eeg_samples.append(sample2)
        return EEGMessage(msgId, eeg_samples)

    def __init__(self, msgId, eeg_samples):
        self.msgId = msgId
        self.eeg_samples = eeg_samples


eeg_samples = []
file_path = "logs/proto_json_chip_all.log"
with open(file_path, "r") as f:
    for line in f:
        msg = EEGMessage.from_json(json.loads(line))
        eeg_samples.extend(msg.eeg_samples)

# eeg_samples = sorted(eeg_samples, key=lambda x: x.timestamp)

cur_timestamp = None
for eeg_data in eeg_samples:
    if cur_timestamp is not None and eeg_data.timestamp != cur_timestamp + 1:
        logger.error(
            f"timestamp not auto increment: {cur_timestamp} -> {eeg_data.timestamp}"
        )
    cur_timestamp = eeg_data.timestamp
