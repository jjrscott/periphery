
PATH_ROOT=$1 # eg '/Users/bob/Repositories/periphery/Sources/Frontend/'

./generate_file_graph.py graph.json --path-root $PATH_ROOT | mmdc --input - --output frontend_file_graph.svg
./generate_file_graph.py --cluster graph.json --path-root $PATH_ROOT| mmdc --input - --output frontend_file_graph_custered.svg
./generate_type_graph.py graph.json | mmdc --input - --output frontend_type_graph.svg
