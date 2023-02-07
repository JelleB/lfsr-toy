import torch

class XORTapModel(torch.nn.Module):
  def __init__(self, taps):
    super(XORTapModel, self).__init__()
    self.taps = taps

  def forward(self, x):
    # Extract the bits at the tap positions
    tap_bits = [x[:, tap] for tap in self.taps]
    # Compute the XOR of the tap bits
    xor = tap_bits[0]
    for tap_bit in tap_bits[1:]:
      xor = torch.bitwise_xor(xor, tap_bit)
    # Return the XOR result as a 1-bit output
    return xor

# Instantiate the model with specific tap positions
model = XORTapModel([0, 5, 12, 24, 48])

# Test the model
inputs = torch.randint(2, size=(64, 64))
outputs = model(inputs)
print(outputs)  # should print a tensor of size (64, 1) with 1-bit XOR values


# import torch
#
# class XORModel(torch.nn.Module):
#   def __init__(self):
#     super(XORModel, self).__init__()
#
#   def forward(self, x, y):
#     return x ^ y
#
# # Instantiate the model
# model = XORModel()
#
# # Test the model
# inputs = [(0, 0), (0, 1), (1, 0), (1, 1)]
# outputs = [model(x, y) for x, y in inputs]
#
# print(outputs)  # should print [0, 1, 1, 0]