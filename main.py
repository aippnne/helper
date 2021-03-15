from JDHelper import JDHelper
import sys

if __name__ == '__main__':
    # choice = input('功能选择:\n  1.预约\n  2.抢购\n')
    choice = '2'

    helper = JDHelper()

    if choice == '1':
        helper.reserve()
    elif choice == '2':
        helper.pool_executor()
    else:
        print('没有此功能')
        sys.exit(1)