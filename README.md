A python program to print a die-cut asset label on the QL-800 label maker with a title and barcode.

To run:

	`python3 print_label.py "{label description}" "{13 digit barcode #}"`

e.g.

	`python3 print_label.py "USB Mouse" "0000000012345"

## Implementation
The label is generated using Pillow and saved to a local file for printing using the brother_ql python library,
which sends direct raster instructions to the printer (unfortunatelly the QL-800 has no good cups driver).

`brother_ql` contains a forked copy of https://github.com/pk aus/brother_ql which adds a label definition for the DK3235
remoavable adhesive die-cut labels that we prefer to use for asset management. 
