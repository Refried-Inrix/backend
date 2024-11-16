{
  inputs.nixpkgs.url = "nixpkgs";

  outputs = { self, nixpkgs, }:
    let
      lib = nixpkgs.lib;
      systems = [ "aarch64-linux" "x86_64-linux" ];
      eachSystem = f:
        lib.foldAttrs lib.mergeAttrs { }
        (map (s: lib.mapAttrs (_: v: { ${s} = v; }) (f s)) systems);
    in eachSystem (system:
      let pkgs = import nixpkgs { inherit system; };
      in {
        devShells.default = pkgs.mkShell {
          inputsFrom = [ ];

          packages = with pkgs; [ 
            python3
            python312Packages.flask
            python312Packages.mysql-connector
            valgrind
            strace
          ];
        };

        packages = {
          # default = neon.neomacs;
        };
      });
}
