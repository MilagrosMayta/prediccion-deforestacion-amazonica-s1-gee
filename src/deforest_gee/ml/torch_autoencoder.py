def construir_autoencoder(in_channels: int = 2, latent_channels: int = 32):
    try:
        import torch.nn as nn
    except ImportError as exc:
        raise RuntimeError("Instale PyTorch con: python -m pip install -e \".[torch]\"") from exc

    class Autoencoder(nn.Module):
        def __init__(self):
            super().__init__()
            self.encoder = nn.Sequential(
                nn.Conv2d(in_channels, 16, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
                nn.Conv2d(16, latent_channels, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
            )
            self.decoder = nn.Sequential(
                nn.ConvTranspose2d(latent_channels, 16, 2, stride=2), nn.ReLU(),
                nn.ConvTranspose2d(16, in_channels, 2, stride=2),
            )

        def forward(self, x):
            return self.decoder(self.encoder(x))

    return Autoencoder()
