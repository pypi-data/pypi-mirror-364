class ViewsTools:
    @classmethod
    def msg(cls, code, msg=None, data=None, **kwargs):
        result = dict()
        result['code'] = int(code) if str(code).isdigit() else 50000
        result['msg'] = kwargs.get('remsg', None) or msg
        if data is not None:
            result['data'] = data
        return result
