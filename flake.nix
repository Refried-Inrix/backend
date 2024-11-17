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
            (pkgs.python3.withPackages (python-pkgs: with python-pkgs; [
              # pandas requests
              flask
              boto3
              psycopg2
            ]))
            # postgresql_16
          ];
        };

        packages = {
          # default = neon.neomacs;
        };
      });
}
