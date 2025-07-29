from bluer_ugv.parts.classes import Part, PartDB

db_of_parts: PartDB = PartDB()

db_of_parts["330-ohm"] = [
    "Resistor, 330-470 Ω, 1/4 watt, 5% tolerance",
]

db_of_parts["4-ch-transceiver"] = Part(
    info=[
        "4-channel transmitter and receiver",
        "source: [digikala](https://www.digikala.com/product/dkp-11037586/%DA%AF%DB%8C%D8%B1%D9%86%D8%AF%D9%87-%D9%88-%D9%81%D8%B1%D8%B3%D8%AA%D9%86%D8%AF%D9%87-%D9%85%D8%A7%D8%B4%DB%8C%D9%86-%DA%A9%D9%86%D8%AA%D8%B1%D9%84%DB%8C-%D9%85%D8%AF%D9%84-4ch-led/)",
        "voltages: receiver 6 VDC,  transmitter 3 VDC",
    ],
    images="https://github.com/kamangir/assets2/blob/main/bluer-sparrow/parts/4-channel-remote-control/view.png?raw=true?raw=true",
)

db_of_parts["470-mF"] = [
    "capacitor, 470 μF to 1000 μF, 16 V or 25 V, Electrolytic, 105 °C rated if possible."
]

db_of_parts["BTS7960"] = [
    "43 A, H-Bridge Motor Driver",
    "specs: [BTS7960](https://www.handsontec.com/dataspecs/module/BTS7960%20Motor%20Driver.pdf)",
]

db_of_parts["dc-motor-12-VDC-45W"] = [
    "12 VDC motor, 20-45 W, 9000 RPM",
]

db_of_parts["LED"] = [
    "LED, ~2 V forward voltage, 10-20 mA",
]

db_of_parts["Polyfuse"] = [
    "Polyfuse, 1.1 A hold, 2.2 A trip, 16 V, resettable, through-hole, e.g., MF-R110",
]

db_of_parts["rpi3bp"] = [
    "Raspberry Pi 3B+",
]

db_of_parts["SLA-Battery"] = [
    "Rechargeable sealed lead acid battery, 12 V, 7 Ah",
]

db_of_parts["TVS-diode"] = [
    "TVS diode, unidirectional, 600 W, 6.8 V clamp, e.g. P6KE6.8A, DO-15 package",
]

db_of_parts["XL4015"] = [
    "12 VDC -> 5 VDC, 4A",
    "specs: [XL4015](https://www.handsontec.com/dataspecs/module/XL4015-5A-PS.pdf)",
]

db_of_parts["rpi-camera"] = [
    "Raspberry Pi Camera, V1.3"
    "https://www.raspberrypi.com/documentation/accessories/camera.html",
]

db_of_parts["DC-gearboxed-motor-12V-120RPM"] = Part(
    info=[
        "Gearboxed DC Motor, 12 V (3-24 V), 3A, 120 RPM, 1:91, 15 Kg cm",
        "[GM6558](https://www.landaelectronic.com/product/%d9%85%d9%88%d8%aa%d9%88%d8%b1-dc-%da%af%db%8c%d8%b1%d8%a8%da%a9%d8%b3-%d8%ad%d9%84%d8%b2%d9%88%d9%86%db%8c-gm6558/)",
    ],
    images=[
        "https://github.com/kamangir/assets2/blob/main/bluer-sparrow/parts/GM6558/01.jpg?raw=true",
        "https://github.com/kamangir/assets2/blob/main/bluer-sparrow/parts/GM6558/02.jpg?raw=true",
        "https://github.com/kamangir/assets2/blob/main/bluer-sparrow/parts/GM6558/03.jpg?raw=true",
        "https://github.com/kamangir/assets2/blob/main/bluer-sparrow/parts/GM6558/04.jpg?raw=true",
        "https://github.com/kamangir/assets2/blob/main/bluer-sparrow/parts/GM6558/measurements.jpg?raw=true",
        "https://github.com/kamangir/assets2/blob/main/bluer-sparrow/parts/GM6558/specs.png?raw=true",
    ],
)
