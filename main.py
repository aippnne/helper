from JDHelper import JDHelper
from utils import Timer
import sys

if __name__ == '__main__':
    choice = input('功能选择:\n  1.预约\n  2.抢购\n  3.同步时间\n')
    # choice = '2'

    helper = JDHelper()

    if choice == '1':
        helper.reserve()
    elif choice == '2':
        helper.toCart()
        helper.pool_executor()
    elif choice == '3':
        timer = Timer()
        timer.time_sync()
    else:
        print('没有此功能')
        sys.exit(1)