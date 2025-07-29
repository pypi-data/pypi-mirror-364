import torch
import numpy as np
from torch.utils.data import Dataset


class UTKFaceHFDataset(Dataset):
    def __init__(self, hf_ds, transform=None):
        self.ds = hf_ds
        self.transform = transform
        #self.indices = list(range(len(self.ds)))
        self.indices = [i for i, row in enumerate(hf_ds)
                        if row["jpg.chip.jpg"] is not None]
    def __len__(self):
        return len(self.indices)

    def __getitem__(self, idx):
      row = row = self.ds[self.indices[idx]]
      img = row["jpg.chip.jpg"].convert("RGB")
      if self.transform:
          img = self.transform(img)
      else:
          img = torch.from_numpy(np.array(img)).permute(2,0,1).float() / 255.0

      key = row["__key__"]
      parts = key.split("/")[1].split("_")
      age, gender, race = map(int, parts[:3])

      return img, torch.tensor(age, dtype=torch.float)