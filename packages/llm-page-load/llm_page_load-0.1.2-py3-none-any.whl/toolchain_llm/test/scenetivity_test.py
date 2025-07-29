from scenetivity import replace
from utils import test_logger

def test_replace():
    text = "商品123，价格456，liyilun02@meituan.com"
    test_logger.info(replace(text))
    assert replace(text)=="商品1*，价格456，*某邮箱*"
