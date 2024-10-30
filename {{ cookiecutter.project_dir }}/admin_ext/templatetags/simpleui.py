from simpleui.templatetags import simpletags


@simpletags.register.simple_tag(takes_context=True)
def menus(context, _get_config=None):
    data = []

    if not _get_config:
        _get_config = simpletags.get_config

    config = _get_config('SIMPLEUI_CONFIG')
    config = {} if not config else config.copy()

    app_list = context.get('app_list')
    for app in app_list:
        _models = (
            [
                {
                    'name': m.get('name'),
                    'icon': simpletags.get_icon(m.get('object_name'), simpletags.unicode_to_str(m.get('name'))),
                    'url': m.get('admin_url'),
                    'addUrl': m.get('add_url'),
                    'breadcrumbs': [
                        {
                            'name': app.get('name'),
                            'icon': simpletags.get_icon(app.get('app_label'), app.get('name')),
                        },
                        {
                            'name': m.get('name'),
                            'icon': simpletags.get_icon(m.get('object_name'), simpletags.unicode_to_str(m.get('name'))),
                        },
                    ],
                }
                for m in app.get('models')
            ]
            if app.get('models')
            else []
        )

        module = {
            'name': app.get('name'),
            'icon': simpletags.get_icon(app.get('app_label'), app.get('name')),
            'models': _models,
        }
        data.append(module)

    if not context.request.user.is_superuser and simpletags.has_permission_in_config(config):
        config['menus'] = simpletags.get_filtered_menus(config['menus'], context.request.user.get_all_permissions())

    # 如果有menu 就读取，没有就调用系统的
    key = 'system_keep'
    if config and 'menus' in config:
        if config.get(key, None):
            temp = config.get('menus')
            for i in temp:
                # 处理面包屑
                if 'models' in i:
                    for k in i.get('models'):
                        k['breadcrumbs'] = [
                            {
                                'name': i.get('name'),
                                'icon': i.get('icon'),
                            },
                            {
                                'name': k.get('name'),
                                'icon': k.get('icon'),
                            },
                        ]
                else:
                    i['breadcrumbs'] = [
                        {
                            'name': i.get('name'),
                            'icon': i.get('icon'),
                        },
                    ]
                data.append(i)
        else:
            data = config.get('menus')

    # 获取侧边栏排序, 如果设置了就按照设置的内容排序, 留空则表示默认排序以及全部显示
    if config.get('menu_display') is not None:
        display_data = []
        for _app in data:
            if _app['name'] not in config.get('menu_display'):
                continue
            _app['_weight'] = config.get('menu_display').index(_app['name'])
            display_data.append(_app)
        display_data.sort(key=lambda x: x['_weight'])
        data = display_data

    # 给每个菜单增加一个唯一标识，用于tab页判断
    eid = 1000
    simpletags.handler_eid(data, eid)
    menus_string = simpletags.json.dumps(data, cls=simpletags.LazyEncoder)

    # 把data放入session中，其他地方可以调用
    if not isinstance(context, dict) and context.request:
        context.request.session['_menus'] = menus_string

    return f'<script type="text/javascript">var menus={menus_string}</script>'
