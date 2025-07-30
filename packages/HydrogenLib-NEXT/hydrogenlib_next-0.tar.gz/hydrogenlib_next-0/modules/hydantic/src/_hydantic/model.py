import warnings
from collections import OrderedDict
from typing import Unpack, Iterable

from _hycore.data_structures import Visited
from _hycore.typefunc import iter_annotations, iter_attributes
from .models import _FieldValidator, ModelConfig, Field, BaseModelConfig


def field_validator(name):
    def decorator(func):
        return _FieldValidator(func, name)

    return decorator


class BaseModel:
    def __init_subclass__(cls, **kwargs: Unpack[BaseModelConfig]):
        cls.__model__ = model = ModelConfig()
        model.fields = OrderedDict()

        count_optional_field = 0  # 记录有默认值的字段有多少个

        annotations = map(lambda x: Field(*x), iter_annotations(cls))  # type: Iterable[Field]
        for field in annotations:
            model.position_fields[field.name] = field
            if field.is_optional():
                count_optional_field += 1  # 可选参数数量增加

            elif count_optional_field:  # 已有过带默认值的字段,且当前字段不再是默认值字段
                break  # 这时候我们已经跳出了基本的位置参数,该去处理关键字参数了

            # 无事发生时
            setattr(cls, field.name, field)  # 将描述符填充到类中
            model.fields[field.name] = field  # 还有这个

        for field in annotations:
            # 从这里开始, 所有的字段都将变成关键字字段
            # 我们需要将可选和必选的字段分别填充到两个字典中
            if field.is_optional():
                model.keyword_optional_fields[field.name] = field
            else:
                model.keyword_required_fields[field.name] = field

        for name, value in iter_attributes(cls):  # 处理验证器
            if isinstance(value, _FieldValidator):
                if value.name not in model.fields:
                    warnings.warn(f"FieldValidator {value.name} not found in {cls.__name__}")
                    continue  # 跳过这个无效的验证器

                model.fields[value.name].validator = value  # 绑定验证器

    def __init__(self, *args, **kwargs):
        vis = Visited()
        model = self.__model__

        # 位置参数出现问题的情况只有两种: 长了或者短了
        # 长了,那么一定有问题
        if len(model.position_fields) < len(args):  # 传入的参数比所有位置参数多
            raise TypeError('Too many arguments')

        # 反向说明了 len(args) <= len(model.position_fields)
        # 也就是 args 可能缺失了一些可选参数

        items = iter(model.position_fields.items())  # items 是一个迭代器
        for (name, field), arg in zip(items, args):
            setattr(self, field.name, arg)  # 赋值, 验证会自动进行
            vis[name] = True  # 注意标记访问状态

        # 由于过长的情况已经处理过了
        # 所以我们要看看现在的 items 有没有被遍历完
        # 如果没有,则检查后面的是不是可选参数
        # 只需要一次 For 或者一次 next 即可得知
        # 我们用 try + next
        try:
            _, field = next(items)
        except StopIteration:
            field = None

        if field and field.is_required():
            raise TypeError(f'Missing arguments')

        # 该处理 kwargs 了

        missing_keys = set()
        unexcept_keys = set()
        typeerr_dct = {}

        error = False

        extra_mode = model.extra_mode
        for name, field in model.fields.items():  # 遍历 kwargs 字典
            value = kwargs.get(name)
            if value is None:
                if field.is_required():
                    missing_keys.add(name)
                    error = True
                # 缺失的可选参数: 忽略

            setattr(self, name, value)  # 直接赋值
            # Field 会自动进行验证

    def from_dict(self, dct):
        self.__init__(**dct)

    def dict(self):
        return {
            name: getattr(self, name)
            for name in self.__model__.fields
        }
