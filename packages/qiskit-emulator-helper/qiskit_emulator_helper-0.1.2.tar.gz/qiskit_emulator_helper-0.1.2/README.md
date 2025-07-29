# Qiskit Emulator Helper

A utility library for easily **searching, recommending, and retrieving fake backends / emulators** from `qiskit-ibm-runtime`.

## Installation

To install the library from the local source code, clone the repository and run `pip`:

```bash
pip install -e .
```

Alternatively, users can install it via:

```bash
pip install qiskit-emulator-helper
```

## Usage

After installation, you can import and use the library with the following name:

```python
import qiskit_emulator_helper as qeh

# 1. List all available emulators
print("--- Listing all available emulators ---")
qeh.show_available_backends()

# 2. Recommend an emulator for a 7-qubit circuit
print("\n--- Proposing an emulator for 7 qubits ---")
qeh.propose_backends(num_qubits=7)

# 3. Retrieve a specific emulator by name
print("\n--- Getting the 'fake_manila' emulator ---")
try:
    backend = qeh.get_backend_by_name('fake_manila')
    print(f"Successfully retrieved: {backend.name}")
    print(f"Number of qubits: {backend.target.num_qubits}")
except ValueError as e:
    print(e)
```
