import abc


class GraphAbstract(object, metaclass=abc.ABCMeta):
    """グラフ処理を定義するための基底クラス"""
    @abc.abstractmethod
    def plot_graph(self, *args):
        pass
