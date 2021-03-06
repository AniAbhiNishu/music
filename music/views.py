from django.views import generic
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth import authenticate, login , logout
from django.views.generic import View
from .forms import UserForm,SongForm
from .models import Album, Song


def index(request):
    if not request.user.is_authenticated():
        return render(request, 'music/login_page.html')
    else:
        albums = Album.objects.all()
        return render(request, 'music/index.html', {'all_albums': albums})


def SongsView(request):
    if not request.user.is_authenticated():
        return render(request, 'music/login_page.html')
    else:
        all_songs = Song.objects.all()
        return render(request, 'music/music_list.html',{'all_songs':all_songs})
  
class DetailView(generic.DetailView):
      model=Album
      template_name= 'music/detail.html'


class AlbumCreate(CreateView):
      model=Album
      fields =['artist', 'album_title', 'genre','album_logo']

class AlbumUpdate(UpdateView):
      model=Album
      fields =['artist', 'album_title', 'genre','album_logo']

class AlbumDelete(DeleteView):
      model=Album
      success_url = reverse_lazy('music:index')


def create_song(request, album_id):
    form = SongForm(request.POST or None, request.FILES or None)
    album = get_object_or_404(Album, pk=album_id)
    if form.is_valid():
        albums_songs = album.song_set.all()
        for s in albums_songs:
            if s.song_title == form.cleaned_data.get("song_title"):
                context = {
                    'album': album,
                    'form': form,
                    'error_message': 'You already added that song',
                }
                return render(request, 'music/song_form.html', context)
        song = form.save(commit=False)
        song.album = album
        song.save()
        return render(request, 'music/detail.html', {'album': album})
    context = {
        'album': album,
        'form': form,
    }
    return render(request, 'music/song_form.html', context)

class SongDelete(DeleteView):
      model= Song
      success_url = reverse_lazy('music:music_list')

class UserFormView(View):
      form_class=UserForm
      template_name= 'music/registration_form.html'

      #display blank form
      def get(self,request):
          form = self.form_class(None)
          return render(request, self.template_name, {'form': form})
      
      # process form data
      def post(self, request):
          form =self.form_class(request.POST)  
   
          if form.is_valid():

             user= form.save(commit=False)

             # cleaned (normalized data)      
             username= form.cleaned_data['username']
             password= form.cleaned_data['password']
             user.set_password(password)
             user.save()
  
             # returns User objects if credentials are correct
             user= authenticate(username=username, password=password)



             if user is not None:
                if user.is_active:
                   login(request, user)
                   return redirect('music:index')
          return render(request, self.template_name, {'form': form})
      
def logout_user(request):
    logout(request)
    form = UserForm(request.POST or None)
    context = {
        "form": form,
    }
    return render(request, 'music/login_page.html', context)


def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                albums = Album.objects.all()
                return render(request, 'music/index.html', {'all_albums':albums , 'username':username })
            else:
                return render(request, 'music/login_page.html', {'error_message': 'Your account has been disabled'})
        else:
            return render(request, 'music/login_page.html', {'error_message': 'Invalid login'})
    return render(request, 'music/login_page.html')
