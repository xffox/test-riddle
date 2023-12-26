{
  description = "test-riddle";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils, ... }:
  flake-utils.lib.eachDefaultSystem (system:
    let pkgs = nixpkgs.legacyPackages.${system};
        pythonPkgs = pkgs.python3Packages;
    in {
      packages = {
        default = pkgs.callPackage ./build.nix {};
      };
      devShells = {
        default = pkgs.mkShell {
          packages = with pythonPkgs; [
            python-lsp-server
            pyflakes
            mypy
            pylint
          ];
        };
      };
  });
}
