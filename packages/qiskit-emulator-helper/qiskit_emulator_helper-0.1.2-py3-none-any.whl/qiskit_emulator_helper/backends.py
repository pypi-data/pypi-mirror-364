# qiskit_emulator_helper/backends.py

import inspect
import qiskit_ibm_runtime.fake_provider as fake_provider

_BACKENDS = dict()

def _initialize_backends():
    """Initializes and catalogs all available fake backends."""
    for name, cls in inspect.getmembers(fake_provider, inspect.isclass):
        if name.startswith("Fake") and hasattr(cls, "target"):
            backend = cls()
            num_qubits = backend.target.num_qubits
            
            if num_qubits not in _BACKENDS:
                _BACKENDS[num_qubits] = dict()
            _BACKENDS[num_qubits][backend.name] = backend

_initialize_backends()

def get_all_backends():
    """Returns a dictionary of all found fake backends."""
    return _BACKENDS

def show_available_backends():
    """Displays available fake backends grouped by their qubit count."""
    print("Available fake backends (emulators):")
    for num_qubits, backends in sorted(_BACKENDS.items()):
        print(f"Qubits: {num_qubits}")
        for backend_name in sorted(backends.keys()):
            print(f"  - {backend_name}")

def propose_backends(num_qubits: int, print_info: bool = True):
    """Proposes a suitable backend based on the number of qubits."""
    if num_qubits in _BACKENDS:
        if print_info:
            print(f"✅ Found emulators with exactly {num_qubits} qubits:")
            for backend_name in _BACKENDS[num_qubits]:
                print(f"  - {backend_name}")
        return _BACKENDS[num_qubits]

    larger_backends_qubits = sorted([q for q in _BACKENDS if q > num_qubits])
    
    if not larger_backends_qubits:
        if print_info:
            print(f"❌ No emulator available with {num_qubits} qubits or more.")
        else:
            raise ValueError(f"No emulator available with {num_qubits} qubits or more.")
    
    list_available_backends = []
    if print_info:
        print(f"ℹ️ No emulator with exactly {num_qubits} qubits. Proposing larger alternatives:")
    for available_qubits in larger_backends_qubits:
        if print_info:
            print(f"Qubits: {available_qubits}")
            for backend_name in _BACKENDS[available_qubits]:
                print(f"  - {backend_name}")
        list_available_backends += _BACKENDS[available_qubits]
    return list_available_backends
            
def get_backend_by_name(backend_name: str):
    """Gets a backend instance by its name."""
    for num_qubits in _BACKENDS:
        if backend_name in _BACKENDS[num_qubits]:
            return _BACKENDS[num_qubits][backend_name]
    
    raise ValueError(f"Emulator '{backend_name}' not found.")
