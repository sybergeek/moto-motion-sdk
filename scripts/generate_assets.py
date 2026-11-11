from pathlib import Path

from moto_motion.assets import write_f1_car_svg
from moto_motion.icons import write_icon_svgs


if __name__ == "__main__":
    path = write_f1_car_svg(Path("assets/generated/f1_car.svg"))
    print(path)
    for icon_path in write_icon_svgs(Path("assets/generated/icons")):
        print(icon_path)
