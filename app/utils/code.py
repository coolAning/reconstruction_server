class ResponseCode(object):
    Success = 0  # 成功
    Fail = -1  # 失败
    SystemError = 40000  # 系统异常
    NoResourceFound = 40001  # 未找到资源
    InvalidParameter = 40002  # 参数无效
    AccountOrPassWordErr = 40003  # 账户或密码错误
    VerificationCodeError = 40004  # 验证码错误
    PleaseSignIn = 40005  # 请登陆
    WeChatAuthorizationFailure = 40006  # 微信授权失败
    InvalidOrExpired = 40007  # 验证码过期
    MobileNumberError = 40008  # 手机号错误
    FrequentOperation = 40009  # 操作频繁,请稍后再试
    PasswordError = 40010  # 密码错误
    AccountDuplicate = 40011  # 账号重复
    CaptchaSendTooFrequent = 40012  # 验证码发送过于频繁
    


class ResponseMessage(object):
    Success = "成功"
    Fail = "失败"
    SystemError = "系统异常"
    NoResourceFound = "未找到资源"
    InvalidParameter = "参数无效"
    AccountOrPassWordErr = "账户或密码错误"
    VerificationCodeError = "验证码错误"
    PleaseSignIn = "请登陆"
    PasswordError = "密码错误"
    AccountDuplicate = "账号重复"
    CaptchaSendTooFrequent = "验证码发送过于频繁"
