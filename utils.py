class JsonicDecorator(object):

    def __init__(self, *args, **kwargs):
        self.kwargs = kwargs

    def __call__(self, fn):
        def jsoner(obj, **kwargs):
            dic = {}
            key = None
            attr = None
            recurse_limit = 2
            fields = obj._meta.get_all_field_names()
            kwargs.update(self.kwargs)  # ??

            recurse = kwargs.get('recurse', 0)
            incl = kwargs.get('include')
            sk = kwargs.get('skip')
            if incl:
                isinstance(incl, list)
                if isinstance(incl, list):
                    fields.extend(incl)
                else:
                    fields.append(incl)
            if sk:
                if isinstance(sk, list):
                    for skipper in sk:
                        if skipper in fields:
                            fields.remove(skipper)
                else:
                    if sk in fields:
                        fields.remove(sk)

            for f in fields:
                try:
                    attr = getattr(obj, "%s_set" % f)
                except AttributeError:
                    try:
                        attr = getattr(obj, f)
                    except AttributeError:
                        pass
                    except ObjectDoesNotExist:
                        pass
                    else:
                        key = str(f)
                except ObjectDoesNotExist:
                    pass
                else:
                    key = "%s_set" % f

                if key:
                    if hasattr(attr, "__class__") and hasattr(attr, "all"):
                        if callable(attr.all):
                            if hasattr(attr.all(), "json"):
                                if recurse < recurse_limit:
                                    kwargs['recurse'] = recurse + 1
                                    dic[key] = attr.all().json(**kwargs)
                    elif hasattr(attr, "json"):
                        if recurse < recurse_limit:
                            kwargs['recurse'] = recurse + 1
                            dic[key] = attr.json(**kwargs)
                    else:
                        try:
                            unicode = attr.__str__()
                        except UnicodeEncodeError:
                            unicode = attr.encode('utf-8')
                        dic[key] = unicode

            if hasattr(obj, "_ik"):
                if hasattr(obj, obj._ik.image_field):
                    if hasattr(getattr(obj, obj._ik.image_field), 'size'):
                        if getattr(obj, obj._ik.image_field):
                            for accessor in [getattr(obj, s.access_as) for s in obj._ik.specs]:
                                key = accessor.spec.access_as
                                dic[key] = {
                                    'url': accessor.url,
                                    'width': accessor.width,
                                    'height': accessor.height,
                                }
            return fn(obj, json=dic, **kwargs)

        return jsoner
