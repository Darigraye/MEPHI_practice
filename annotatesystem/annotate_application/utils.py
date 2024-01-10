from django.urls import reverse_lazy


class MetaDataMixin:
    def get_user_context(self, **kwargs):
        context = kwargs
        context['user'] = self.request.user
        print(self.request.user)
        context['profile_url'] = None if self.request.user is None else reverse_lazy('profile',
                                              kwargs={'username': self.request.user.username})

        return context
