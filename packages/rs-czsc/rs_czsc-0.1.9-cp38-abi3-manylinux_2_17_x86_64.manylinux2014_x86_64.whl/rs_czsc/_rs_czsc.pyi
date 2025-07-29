from enum import IntEnum
from typing import Union


class PyWeightBacktest:
    @classmethod
    def __init__(cls, *args, **kwargs) -> None: ...
    @staticmethod
    def from_arrow(*args, **kwargs): ...
    @staticmethod
    def from_raw(*args, **kwargs): ...
    def stats(self, *args, **kwargs): ...
    def daily_return(self, *args, **kwargs): ...
    def dailys(self, *args, **kwargs): ...
    def alpha(self, *args, **kwargs): ...
    def pairs(self, *args, **kwargs): ...


def daily_performance(daily_returns: list[float], yearly_days: Union[None, int] = None):
    """采用单利计算日收益数据的各项指标

    函数计算逻辑：

    1. 首先，将传入的日收益率数据转换为NumPy数组，并指定数据类型为float64。
    2. 然后，进行一系列判断：如果日收益率数据为空或标准差为零或全部为零，则返回字典，其中所有指标的值都为零。
    3. 如果日收益率数据满足要求，则进行具体的指标计算：

        - 年化收益率 = 日收益率列表的和 / 日收益率列表的长度 * 252
        - 夏普比率 = 日收益率的均值 / 日收益率的标准差 * 标准差的根号252
        - 最大回撤 = 累计日收益率的最高累积值 - 累计日收益率
        - 卡玛比率 = 年化收益率 / 最大回撤（如果最大回撤不为零，则除以最大回撤；否则为10）
        - 日胜率 = 大于零的日收益率的个数 / 日收益率的总个数
        - 年化波动率 = 日收益率的标准差 * 标准差的根号252
        - 下行波动率 = 日收益率中小于零的日收益率的标准差 * 标准差的根号252
        - 非零覆盖 = 非零的日收益率个数 / 日收益率的总个数
        - 回撤风险 = 最大回撤 / 年化波动率；一般认为 1 以下为低风险，1-2 为中风险，2 以上为高风险

    4. 将所有指标的值存储在字典中，其中键为指标名称，值为相应的计算结果。

    :param daily_returns: 日收益率数据，样例：
        [0.01, 0.02, -0.01, 0.03, 0.02, -0.02, 0.01, -0.01, 0.02, 0.01]
    :param yearly_days: 一年的交易日数，默认为 252
    :return: dict，输出样例如下

        {'绝对收益': 1.0595,
        '年化': 0.1419,
        '夏普': 0.7358,
        '最大回撤': 0.3803,
        '卡玛': 0.3732,
        '日胜率': 0.5237,
        '日盈亏比': 1.0351,
        '日赢面': 0.0658,
        '年化波动率': 0.1929,
        '下行波动率': 0.1409,
        '非零覆盖': 1.0,
        '盈亏平衡点': 0.9846,
        '新高间隔': 312.0,
        '新高占比': 0.0579,
        '回撤风险': 1.9712,
        '回归年度回报率': 0.1515,
        '长度调整平均最大回撤': 0.446}
    """
    ...


def top_drawdowns(*args, **kwargs): ...


def normalize_feature(*args, **kwargs): ...


class Freq(IntEnum):
    """
    频率
    """

    Tick = 0
    """逐笔"""

    F1 = 1
    """1分钟"""

    F2 = 2
    """2分钟"""

    F3 = 3
    """3分钟"""

    F4 = 4
    """4分钟"""

    F5 = 5
    """5分钟"""

    F6 = 6
    """6分钟"""

    F10 = 7
    """10分钟"""

    F12 = 8
    """12分钟"""

    F15 = 9
    """15分钟"""

    F20 = 10
    """20分钟"""

    F30 = 11
    """30分钟"""

    F60 = 12
    """60分钟"""

    F120 = 13
    """120分钟"""

    D = 14
    """日线"""

    W = 15
    """周线"""

    M = 16
    """月线"""

    S = 17
    """季线"""

    Y = 18
    """年线"""

class Market(IntEnum):
    """市场类型"""

    AShare = 1
    """A股"""

    Futures = 2
    """期货"""

    Default = 3
    """默认"""

class RawBar:
    @classmethod
    def __init__(
        cls,
        symbol: str,
        dt_utc_timestamp: int,
        freq: Freq,
        open: float,
        close: float,
        high: float,
        low: float,
        vol: float,
        amount: float,
    ) -> None: ...

class BarGenerator:
    @classmethod
    def __init__(
        cls,
        base_freq: Freq,
        freqs: list[Freq],
        max_count: int,
        market: Market,
    ) -> None: ...
    def init_freq_bars(self, freq: Freq, bars: list[RawBar]):
        """初始化某个周期的K线序列
        函数计算逻辑：

        1. 首先，它断言`freq`必须是`self.bars`的键之一。如果`freq`不在`self.bars`的键中，代码会抛出一个断言错误。
        2. 然后，它断言`self.bars[freq]`必须为空。如果`self.bars[freq]`不为空，代码会抛出一个断言错误，并显示一条错误消息。
        3. 如果以上两个断言都通过，它会将`bars`赋值给`self.bars[freq]`，从而初始化指定频率的K线序列。
        4. 最后，它会将`bars`列表中的最后一个`RawBar`对象的`symbol`属性赋值给`self.symbol`。

        :param freq: 周期名称
        :param bars: K线序列
        """
        ...

    def get_latest_date(self) -> None | str: ...
    def get_symbol(self) -> None | str: ...
    def update(self, bar: RawBar):
        """更新各周期K线

        函数计算逻辑：

        1. 首先，它获取基准频率`base_freq`，并断言`bar`的频率值等于`base_freq`。
        2. 然后，它将`bar`的符号和日期时间设置为`self.symbol`和`self.end_dt`。
        3. 接下来，它检查是否已经有一个与`bar`日期时间相同的K线存在于`self.bars[base_freq]`中。
            如果存在，它会记录一个警告并返回，不进行任何更新。
        4. 如果不存在重复的K线，它会遍历`self.bars`的所有键（即所有的频率），并对每个频率调用`self._update_freq`方法来更新该频率的K线。
        5. 最后，它会限制在内存中的K线数量，确保每个频率的K线数量不超过`self.max_count`。

        :param bar: 必须是已经结束的Bar
        :return: None
        """
        ...
    # @property
    # def symbol(self) -> None | str:
    #     return self.get_symbol()

    # @property
    # def end_dt(self) -> None | str:
    #     return self.get_latest_date()

def print_it(*args, **kwargs): ...
