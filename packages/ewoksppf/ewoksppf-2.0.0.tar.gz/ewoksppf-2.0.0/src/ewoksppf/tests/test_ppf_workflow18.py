import pytest
from ewoksppf import execute_graph
from ewokscore.tests.utils.results import assert_execute_graph_default_result


def workflow18(dotask4=True):
    ppfmethod = "ewoksppf.tests.test_ppf_actors.pythonActorAddWithoutSleep.run"
    nodes = [
        {
            "id": "task1",
            "task_type": "ppfmethod",
            "task_identifier": ppfmethod,
            "default_inputs": [{"name": "value", "value": 0}],
        },
        {
            "id": "task2",
            "task_type": "ppfmethod",
            "task_identifier": ppfmethod,
            "default_inputs": [{"name": "value", "value": 10}],
        },
        {"id": "task3", "task_type": "ppfmethod", "task_identifier": ppfmethod},
        {"id": "task4", "task_type": "ppfmethod", "task_identifier": ppfmethod},
    ]
    links = [
        {"source": "task1", "target": "task3", "map_all_data": True},
        {"source": "task2", "target": "task3"},
        {
            "source": "task2",
            "target": "task4",
            "map_all_data": True,
            "conditions": [{"source_output": "value", "value": 11 if dotask4 else 0}],
        },
    ]
    graph = {
        "graph": {"id": "workflow18"},
        "links": links,
        "nodes": nodes,
    }

    if dotask4:
        expected_results = {"_ppfdict": {"value": 12}}
    else:
        expected_results = {"_ppfdict": {"value": 2}}

    return graph, expected_results


@pytest.mark.parametrize("dotask4", [True, False])
def test_workflow18(dotask4, ppf_log_config, tmpdir):
    """Test conditional links"""
    varinfo = {"root_uri": str(tmpdir)}
    graph, expected = workflow18(dotask4=dotask4)
    result = execute_graph(graph, varinfo=varinfo)
    assert_execute_graph_default_result(graph, result, expected, varinfo=varinfo)
