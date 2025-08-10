{ pkgs }: {
  deps = [
    pkgs.bash
    pkgs.python311
    pkgs.python311Packages.pip
    pkgs.nodejs_20
    pkgs.nodePackages.npm
    pkgs.sqlite
  ];
}