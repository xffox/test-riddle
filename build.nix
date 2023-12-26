{lib, python3Packages}:
python3Packages.buildPythonApplication {
  pname = "test-riddle";
  version = "0.1";
  pyproject = true;
  src = ./.;
  nativeBuildInputs = [
    python3Packages.setuptools
  ];
}
