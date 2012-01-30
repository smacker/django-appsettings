# Create your views here.
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.admin.views.decorators import staff_member_required
from settingsobj import Settings
settingsinst = Settings()
from models import Setting
import forms

def get_apps(settingsinst):
    app_list = []
    apps = vars(settingsinst).items()
    for name, app in apps:
        groups = []
        for group_name, group in app._vals.iteritems():
            if group._readonly:continue
            groups.append([group_name, group])
        app_list.append([name, groups])
    return app_list


@staff_member_required
def app_index(request, template = 'appsettings/index.html', base_template = 'index.html'):
    apps = get_apps(settingsinst)
    return render_to_response(template,
            {'app_list':apps, 'base_template':base_template},
            RequestContext(request))

@staff_member_required
def app_settings(request, app_name=None, template = 'appsettings/index.html', base_template = 'index.html'):
    apps = []
    groups = []
    app = getattr(settingsinst, app_name)
    for group_name, group in app._vals.iteritems():
        if group._readonly:continue
        groups.append([group_name, group])
    apps.append([app_name, groups])
    return render_to_response(template,
            {'app_list':apps, 'base_template':base_template, 'app_name':app_name},
            RequestContext(request))

def app_group_settings(request, app_name, group_name, template = 'appsettings/settings.html', base_template = 'index.html'):
    fields = {}
    fieldsets = []
    initial = {}

    app = getattr(settingsinst, app_name)
    group = app._vals[group_name]
    fieldset_fields = []
    for key, value in group._vals.iteritems():
        field_name = u'%s-%s-%s' % (app_name, group_name, key)
        fields[field_name] = value
        fieldset_fields.append(field_name)
        initial[field_name] = getattr(group, key)
    fieldset_fields.sort()
    fieldsets.append((group_name, group._verbose_name, fieldset_fields,))
    editor = type('SettingsForm', (forms.FieldsetForm,),
                     {'base_fieldsets': fieldsets, 'base_fields':fields})
    if request.POST:
        form = editor(request.POST)
        if form.is_valid():
            for key, value in form.fields.iteritems():
                app, group, name = key.split('-')
                val = form.cleaned_data[key]
                if val != getattr(settingsinst, app)._vals[group]._vals[name].initial:
                    setattr(getattr(settingsinst, app)._vals[group], name, val)
    else:
        form = editor(initial)
    return render_to_response(template,
                              {'app':app_name, 'group':group_name, 'form':form, 'base_template':base_template},
                              context_instance=RequestContext(request))
