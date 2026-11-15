import os

if 'data_exporter' not in globals():
    from mage_ai.data_preparation.decorators import data_exporter
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test


@data_exporter
def export_metrics(metrics_df, *args, **kwargs):
    metrics_df.to_csv('iris_metrics.csv', index=False)
    print('Saved', len(metrics_df), 'metrics to iris_metrics.csv')
    return metrics_df


@test
def test_metrics_saved(output, *args):
    assert os.path.exists('iris_metrics.csv'), 'iris_metrics.csv was not created'
    assert len(output) == 4, 'Expected 4 rows in metrics table'
