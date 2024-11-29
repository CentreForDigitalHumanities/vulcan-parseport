from vulcan.data_handling.visualization_type import VisualizationType


class InstanceReader:

    def convert_single_instance(self, instance):
        raise NotImplementedError()

    def convert_instances(self, instances):
        return [self.convert_single_instance(instance) for instance in instances]

    def get_visualization_type(self) -> VisualizationType:
        raise NotImplementedError()


