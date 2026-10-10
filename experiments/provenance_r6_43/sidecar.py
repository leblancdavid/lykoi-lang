"""Pure observation labeling. No VM, execution, oracle or lineage reconstruction."""
from copy import deepcopy
from common import digest

UNAVAILABLE = ('authored_text_line_column', 'expression_occurrence_identity',
               'dynamic_integer_operand_lineage', 'runtime_value_producer_chain')


def label(observation, node_ops, mapping, expansion_paths, flat_pairs=None):
    rows = []
    for index, event in enumerate(observation['events']):
        if event['kind'] == 'charge':
            continue  # raw charge records remain in the committed observation
        node = event['node']
        category = {'decode_raw': 'RAW_BYTE_ORIGIN', 'decode_numeric': 'DECODED_NUMERIC_ORIGIN'}.get(event['kind'])
        if event['kind'] == 'return':
            category = 'SEQUENCE_RETURN_SPAN' if node_ops.get(node) == 'seq' else 'VALUE_SPAN'
        symbolic = ({'status': 'AVAILABLE', 'definition_local': deepcopy(mapping[node]),
                     'expansion_path': deepcopy(expansion_paths[node])}
                    if node in mapping and node in expansion_paths else {'status': 'UNAVAILABLE'})
        cell = event.get('cell')
        row = {'raw_event_index': index, 'raw_node': node, 'category': category,
               'symbolic_origin': symbolic,
               'unavailable': {key: 'UNAVAILABLE' for key in UNAVAILABLE}}
        if cell is not None:
            row['observed_coordinates'] = {'span': deepcopy(cell['span']), 'origins': deepcopy(cell['origins']),
                 'retention': 'AVAILABLE_EMPTY' if not cell['origins'] else 'AVAILABLE'}
        if flat_pairs and node in flat_pairs:
            row['comparison_annotation'] = {'exact_node': flat_pairs[node], 'is_authorship': False}
        rows.append(row)
    return {'version': 'r6_43-observation-1', 'raw_observation_sha256': digest(observation), 'labels': rows,
            'raw_error': deepcopy(observation['envelope'].get('error')),
            'output_span_coordinate_system': 'OUTPUT_BUFFER',
            'unavailable': {key: 'UNAVAILABLE' for key in UNAVAILABLE}}
