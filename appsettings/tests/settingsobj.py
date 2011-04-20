# -*- coding: utf-8 -*-

from django.test import TestCase

from django import forms
import inspect
from appsettings import settingsobj

class TestClass:
    testchar = forms.CharField(initial = 'test value')
    testinteger = forms.IntegerField(initial = 1)
    testfloat = forms.FloatField(initial = 1.5)
    testboolean = forms.BooleanField(initial = True)
    testchoice = forms.ChoiceField(choices = (('val1', 'Name1'),
                                              ('val2', 'Name2')),
                                   initial = 'val1')

class GroupTestCase(TestCase):

    def setUp(self):
        # Set initial to default
        TestClass.testchar.initial = 'test value'

        self.appname = 'testgroup'
        self.name = 'testname'
        classobj = TestClass
        preset = {}
        main = False

        self.group = settingsobj.Group(self.appname, self.name,
                                       classobj, preset, main)

    def test_init(self):
        self.assertEqual(hasattr(self.group, 'testchar'), True)
        self.assertEqual(hasattr(self.group, 'testinteger'), True)
        self.assertEqual(hasattr(self.group, 'testfloat'), True)
        self.assertEqual(hasattr(self.group, 'testboolean'), True)
        self.assertEqual(hasattr(self.group, 'testchoice'), True)

    def test_getattr(self):
        self.assertEqual(self.group.testchar, 'test value')
        self.assertEqual(self.group.testinteger, 1)
        self.assertEqual(self.group.testfloat, 1.5)
        self.assertEqual(self.group.testboolean, True)
        self.assertEqual(self.group.testchoice, 'val1')

    def test_setattr(self):
        self.group.testchar = 'new test value'
        self.assertEqual(self.group.testchar, 'new test value')

    def test_get_no_attr(self):
        self.assertRaises(AttributeError, getattr, self.group, 'no_attr')

    def test_bad_class(self):
        class BadTestClass(TestClass):
            bad_attr =('it', 'cannot', 'contain', 'list')

        classobj = BadTestClass
        preset = {}
        main = False

        self.assertRaises(settingsobj.SettingsException, settingsobj.Group,
                          self.appname, self.name,
                          classobj, preset, main)

    def test_readonly(self):
        self.group._readonly = True

        self.assertRaises(AttributeError, setattr, self.group,
                          'testchar', 'new test value')

    def test_set_no_attr(self):
        self.assertRaises(AttributeError, setattr, self.group, 'no_attr', 'test val')

    def set_to_db(self):
        from appsettings.models import Setting
        from django.contrib.sites.models import Site

        site = Site.objects.get_current()

        setting = Setting(site=site, app=self.appname, class_name=self.name,
                          key='testchar', value='new test value')
        setting.save()

    def test_init_with_db(self):
        self.set_to_db()

        classobj = TestClass
        preset = {}
        main = False

        self.group = settingsobj.Group(self.appname, self.name,
                                       classobj, preset, main)

        self.assertEqual(self.group.testchar, 'new test value')

    def test_set_to_db(self):
        self.set_to_db()
        self.assertEqual(self.group.testchar, 'new test value')

    def test_main_group(self):
        classobj = TestClass
        preset = {}
        main = True

        self.group = settingsobj.Group(self.appname, self.name,
                                       classobj, preset, main)

        # Repeat test
        self.test_init()
        self.test_getattr()
        self.test_setattr()

        # Test correct set settings.py
        from django.conf import settings
        self.assertEqual(settings.testinteger, 1)

        # Test width DB
        self.set_to_db()
        # Update group
        self.group = settingsobj.Group(self.appname, self.name,
                                       classobj, preset, main)

        self.assertEqual(settings.testchar, 'new test value')


class AppTestCase(TestCase):

    def setUp(self):
        appname = 'testapp'
        self.app = settingsobj.App(appname)

    def test_add(self):
        classobj = TestClass
        readonly = False
        main = False
        preset = {}

        self.app._add(classobj, readonly, main, preset)

        self.assertEqual(hasattr(self.app, 'testclass'), True)

    def test_add_bad_name(self):
        class _Add:
            pass

        classobj = _Add
        readonly = False
        main = False
        preset = {}

        self.assertRaises(settingsobj.SettingsException,
                          self.app._add,
                          classobj, readonly, main, preset)

    def test_duplicate_add(self):
        classobj = TestClass
        readonly = False
        main = False
        preset = {}

        self.app._add(classobj, readonly, main, preset)

        self.assertRaises(settingsobj.SettingsException,
                          self.app._add,
                          classobj, readonly, main, preset)

    def test_getattr(self):
        classobj = TestClass
        readonly = False
        main = False
        preset = {}

        self.app._add(classobj, readonly, main, preset)

        self.assertEqual(isinstance(self.app.testclass, settingsobj.Group), True)

    def test_get_no_attr(self):
        self.assertRaises(settingsobj.SettingsException, getattr, self.app, 'no_attr')

    def test_set_no_attr(self):
        self.assertRaises(settingsobj.SettingsException, setattr, self.app, 'no_attr', None)


class SettignsTestCase(TestCase):
    def test_register(self):
        settings = settingsobj.Settings()

        appname = 'test_app'
        classobj = TestClass
        readonly = False
        main = False

        settings._register(appname, classobj, readonly, main)

        self.assertEqual(isinstance(settings.test_app, settingsobj.App), True)
