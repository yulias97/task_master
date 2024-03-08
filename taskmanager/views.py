from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import generic

from taskmanager.forms import TaskSearchForm, TaskForm
from taskmanager.models import Task, Worker


@login_required
def index(request):
    total_tasks = Task.objects.count()
    completed_tasks = Task.objects.filter(is_completed=True).count()
    total_workers = Worker.objects.count()
    context = {
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "total_workers": total_workers,
    }
    return render(request, "taskmanager/index.html", context=context)


class TaskListView(LoginRequiredMixin, generic.ListView):
    paginate_by = 5

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(TaskListView, self).get_context_data(**kwargs)

        name = self.request.GET.get("name", "")
        assignee = self.request.GET.get("assignee", "")
        include_completed = self.request.GET.get("include_completed")

        context["search_form"] = TaskSearchForm(
            initial={
                "name": name,
                "assignee": assignee,
                "include_completed": True if include_completed else False
            }
        )
        return context

    def get_queryset(self):
        queryset = Task.objects.all()
        form = TaskSearchForm(self.request.GET)
        if form.is_valid():
            queryset = queryset.filter(name__icontains=form.cleaned_data["name"])
            if form.cleaned_data["assignee"]:
                queryset = queryset.filter(assignees__username__iexact=form.cleaned_data["assignee"])
            if not form.cleaned_data["include_completed"]:
                queryset = queryset.filter(is_completed=False)
        return queryset


class TaskDetailView(LoginRequiredMixin, generic.DetailView):
    model = Task


class TaskCreateView(LoginRequiredMixin, generic.CreateView):
    model = Task
    form_class = TaskForm
    success_url = reverse_lazy("taskmanager:task-list")


class TaskUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Task
    form_class = TaskForm
    success_url = reverse_lazy("taskmanager:task-list")


class TaskDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Task
    success_url = reverse_lazy("taskmanager:task-list")


class WorkerListView(LoginRequiredMixin, generic.ListView):
    paginate_by = 5
    model = Worker
    success_url = reverse_lazy("taskmanager:worker-list")
