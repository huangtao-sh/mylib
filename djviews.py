# 项目：标准库函数
# 作者：黄涛
# 模块：Django相关
from django.views.generic import ListView,FormView
from django.http import HttpResponseRedirect,HttpResponse
from django.db.models import *

class SearchView(ListView):
    paginate_by=10
    ordering=[]
    extra_context={}
    keywords={}
    search_form_class=None
    initial=None
    def get_context_data(self,**kwargs):
        context=super().get_context_data(**kwargs)
        if self.search_form_class:
            self.extra_context['form']=self.search_form_class(initial=self.initial)
        else:
            self.extra_context['form']=None
        context.update(self.extra_context)
        return context

    def get_queryset(self):
        queryset=super().get_queryset()
        query_filter=self.prepare_filter(self.get_data(self.request.GET))
        queryset=queryset.filter(**query_filter).order_by(
                *self.ordering)
        return queryset

    def get_data(self,data):
        return dict(([(k,data[k]) for k in self.keywords\
                if k in data and data[k] ]))

    def prepare_filter(self,data):
        self.initial=data
        get_str=''.join(['&%s=%s'%(x,data[x]) \
                for x in data])
        self.extra_context['search']=get_str
        r={}
        for k in self.keywords:
            if k in data:
                f=self.keywords.get(k)
                if not f:f='exact'
                r['%s__%s'%(k,f)]=data[k]
        return r

class Report:
    title=None
    column_title=None
    column_class=None
    column_format=None
    data=None
    def as_html(self):
        s=['<table class="report">']
        s.append('<caption>%s</caption>'%(self.title))
        s.append('<tr>')
        s.append('<th>序号</th>')
        for head in self.column_title:
            s.append('<th>%s</th>'%(head))
        s.append('</tr>')

        for a,r in enumerate(self.data):
            s.append('<tr>')
            s.append('<td class="number">%s</td>'%(a+1))
            for i,c in enumerate(r):
                cls=' class="%s">'%(self.column_class[i]) if self.column_class and self.column_class[i] else '>'            
                cls='<td%s'%(cls)
                if self.column_format and self.column_format[i]:
                    c=format(c,self.column_format[i]) if c else ""
                s.append('%s%s</td>'%(cls,c))
            s.append('</tr>')
        s.append('</table>')
        html='\n'.join(s)
        return html
    
class ProcReport(Report):
    proc_name=None
    params=None
    @property
    def data(self):
        from django.db import connection
        cursor=connection.cursor()
        self.params=cursor.callproc(self.proc_name,self.params)
        data=[result for result in cursor.stored_results()]
        return data[0] if len(data) else None
                
        

