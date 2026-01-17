// Main app object
const app = {
    initialized: false,
    apiUrl: `${window.location.origin}/api`,
    currentView: 'menu',
    currentChannel: null,
    currentSeason: null,
    channelPlayer: null,
    vodPlayer: null,

    // Initialize app
    async init() {
        if (this.initialized) return;
        this.initialized = true;

        this.showView('menu');
        this.attachEventListeners();
        console.log('App initialized');
    },

    // View Management
    showView(viewName) {
        // 🔑 Always exit fullscreen when changing views
        exitFullscreenIfNeeded();
        
        // Stop any playing videos when switching views
        document.querySelectorAll('video').forEach(v => {
            v.pause();
            v.removeAttribute('src');
            v.load();
        });
        document.querySelectorAll('video track').forEach(t => t.remove());

        // Hide all views
        document.querySelectorAll('.view').forEach(v => v.classList.add('hidden'));
        document.getElementById('menu').classList.add('hidden');

        // Show the requested view
        if (viewName === 'menu') {
            document.getElementById('menu').classList.remove('hidden');
        } else {
            const view = document.getElementById(viewName);
            if (view) {
                view.classList.remove('hidden');
            }
        }
        this.currentView = viewName;
    },

    goToMenu() {
        this.showView('menu');
    },

    async goToChannels() {
        this.showView('channels-view');
        await this.loadChannels();
    },

    toggleLiveFullscreen() {
        const container = document.querySelector('#channel-player .player-container');
        if (!container) return;

        if (!document.fullscreenElement) {
            container.requestFullscreen().catch(err => {
                console.error('Failed to enter fullscreen:', err);
            });
        } else {
            document.exitFullscreen();
        }
    },



    async goToVOD() {
        this.showView('shows-view');
        const res = await fetch(`${this.apiUrl}/shows`);
        if (!res.ok) throw new Error('Failed to load shows');
        const text = await res.text();
        const shows = JSON.parse(text);
        this.renderShows(shows);
    },

    nextVODEpisode() {
        if (!this.currentSeason) return;

        const episodes = this.currentSeason.episodes;
        if (!episodes.length) return;

        this.currentVODEpisodeIndex =
            (this.currentVODEpisodeIndex + 1) % episodes.length;

        this.playVODEpisode(
            episodes[this.currentVODEpisodeIndex],
            this.currentVODEpisodeIndex
        );
    },

    previousVODEpisode() {
        if (!this.currentSeason) return;

        const episodes = this.currentSeason.episodes;
        if (!episodes.length) return;

        this.currentVODEpisodeIndex =
            (this.currentVODEpisodeIndex - 1 + episodes.length) % episodes.length;

        this.playVODEpisode(
            episodes[this.currentVODEpisodeIndex],
            this.currentVODEpisodeIndex
        );
    },

    renderShows(shows) {
        const grid = document.getElementById('shows-grid');
        grid.innerHTML = '';

        shows.forEach(show => {
            const card = document.createElement('div');
            card.className = 'show-card';
            card.style.backgroundImage =
            `url(http://10.0.0.21:5000/posters/${show.poster})`;

            card.innerHTML = `<div class="title">${show.name}</div>`;
            card.onclick = () => this.selectShow(show);

            grid.appendChild(card);
        });
    },
    
    selectShow(show) {
        this.currentShow = show;
        this.renderSeasons(show.seasons);
        this.showView('vod-view');
    },


    async goToEpisodes() {
        this.showView('vod-episodes');
    },

    // TV Channels
    async loadChannels() {
        try {
            const response = await fetch(`${this.apiUrl}/channels`);
            const channels = await response.json();
            this.renderChannels(channels);
        } catch (error) {
            console.error('Error loading channels:', error);
        }
    },

    renderChannels(channels) {
        const container = document.getElementById('channels-list');
        container.innerHTML = '';

        if (Object.keys(channels).length === 0) {
            container.innerHTML = '<p style="grid-column: 1/-1; text-align: center; padding: 2rem;">No channels added yet</p>';
            return;
        }

        Object.values(channels).forEach(channel => {
            const card = document.createElement('div');
            card.className = 'channel-card';
            card.innerHTML = `
                <h3>📺 ${channel.name}</h3>
                <p>${channel.folder_path}</p>
            `;
            card.onclick = () => this.selectChannel(channel);
            container.appendChild(card);
        });
    },

    async selectChannel(channel) {
        this.currentChannel = channel;
        this.showView('channel-player');
        
        // Initialize channel player
        this.channelPlayer = new ChannelPlayer(channel);
        await this.channelPlayer.initialize();
    },

    // VOD
    renderSeasons(seasons) {
        const container = document.getElementById('seasons-list');
        container.innerHTML = '';

        if (seasons.length === 0) {
            container.innerHTML = '<p style="grid-column: 1/-1; text-align: center; padding: 2rem;">No seasons added yet</p>';
            return;
        }

        seasons.forEach(season => {
            const card = document.createElement('div');
            card.className = 'season-card';
            card.innerHTML = `
                <h3>🎬 ${season.name}</h3>
                <p>${season.episodes.length} episodes</p>
            `;
            card.onclick = () => this.selectSeason(season);
            container.appendChild(card);
        });
    },

    setSubtitle(lang) {
        const video =
            this.currentView === 'channel-player'
                ? document.getElementById('channel-video')
                : document.getElementById('vod-video');

        if (!video) return;

        // 1️⃣ Remove old <track> elements
        [...video.querySelectorAll('track')].forEach(t => t.remove());

        // 2️⃣ Disable ALL existing textTracks (browser keeps them!)
        for (let i = 0; i < video.textTracks.length; i++) {
            video.textTracks[i].mode = 'disabled';
        }

        if (!lang) return;

        const videoApiSrc = video.currentSrc || video.src;
        if (!videoApiSrc.includes('/api/video/')) return;

        const encodedPath = videoApiSrc.split('/api/video/')[1];
        const filePath = decodeURIComponent(encodedPath);
        const basePath = filePath.replace(/\.(mp4|mkv|webm)$/i, '');

        const subtitlePath =
            lang === 'he' ? `${basePath}.vtt`
            : lang === 'en' ? `${basePath}.en.vtt`
            : null;

        if (!subtitlePath) return;

        const subtitleApiUrl = `/api/video/${encodeURIComponent(subtitlePath)}`;

        // 3️⃣ Create new track
        const track = document.createElement('track');
        track.kind = 'subtitles';
        track.label = lang.toUpperCase();
        track.srclang = lang;
        track.src = subtitleApiUrl;
        track.default = true;

        video.appendChild(track);

        // 🔑 FORCE-enable subtitles (reliable)
        setTimeout(() => {
            for (let i = 0; i < video.textTracks.length; i++) {
                const tt = video.textTracks[i];
                tt.mode = (tt.language === lang) ? 'showing' : 'disabled';
            }
        }, 0);
    },

    async selectSeason(season) {
        this.currentSeason = season;
        document.getElementById('season-title').textContent = season.name;
        this.renderEpisodes(season.episodes);
        this.showView('vod-episodes');
    },

    renderEpisodes(episodes) {
        const container = document.getElementById('episodes-list');
        container.innerHTML = '';

        if (episodes.length === 0) {
            container.innerHTML = '<p style="grid-column: 1/-1; text-align: center; padding: 2rem;">No episodes in this season</p>';
            return;
        }

        episodes.forEach((episode, index) => {
            const card = document.createElement('div');
            card.className = 'episode-card';
            card.innerHTML = `
                <h4>Episode ${index + 1}</h4>
                <p>${episode.filename}</p>
            `;
            card.onclick = () => this.playVODEpisode(episode, index);
            container.appendChild(card);
        });
    },

    async playVODEpisode(episode, index) {
        this.currentVODEpisodeIndex = index;
        this.showView('vod-player');

        const video = document.getElementById('vod-video');
        const videoPath = episode.path.replace(/\\/g, '__SLASH__');

        video.pause();
        video.src = `${this.apiUrl}/video/${videoPath}`;

        video.onloadedmetadata = () => {
            video.currentTime = 0;
            video.play();

            // auto fullscreen for VOD
            setTimeout(() => {
                if (!document.fullscreenElement) {
                    document
                    .querySelector('#vod-player .player-container')
                    ?.requestFullscreen()
                    .catch(() => {});
                }
            }, 0);
            
            app.setSubtitle('he');
        };
    },

    toggleVODFullscreen() {
        const container = document.querySelector('#vod-player .player-container');
        if (!container) return;

        if (!document.fullscreenElement) {
            container.requestFullscreen().catch(() => {});
        } else {
            document.exitFullscreen();
        }
    },


    // Event Listeners
    attachEventListeners() {
        let uiTimeout;
        let liveTimeout;

        document.addEventListener('mousemove', () => {
            const playerUI = app.currentView === 'channel-player'
                ? document.querySelector('#channel-player .player-ui')
                : app.currentView === 'vod-player'
                    ? document.querySelector('#vod-player .player-ui')
                    : null;

            const liveIndicator = document.getElementById('live-indicator');

            // Show cursor
            document.body.classList.remove('hide-cursor');

            // Show player UI
            if (playerUI) {
                playerUI.classList.add('visible');
                clearTimeout(uiTimeout);
                uiTimeout = setTimeout(() => {
                    playerUI.classList.remove('visible');
                    document.body.classList.add('hide-cursor'); // 🔥 hide cursor
                }, 3000);
            }

            // Show LIVE badge only on live TV
            if (app.currentView === 'channel-player' && liveIndicator) {
                liveIndicator.classList.add('visible');
                clearTimeout(liveTimeout);
                liveTimeout = setTimeout(() => {
                    liveIndicator.classList.remove('visible');
                }, 3000);
            }
        });
    }
};

// Channel Player Class
class ChannelPlayer {
    constructor(channel) {
        this.channel = channel;
        this.episodes = [];
        this.currentIndex = 0;
        this.video = document.getElementById('channel-video');
        this.episodeInfo = document.getElementById('current-episode-info');
        this.manualOverride = false;
    }

    async initialize() {
        try {
            // Load episodes from channel folder
            const response = await fetch(`${app.apiUrl}/channels/${this.channel.id}/episodes`);
            this.episodes = await response.json();

            if (this.episodes.length === 0) {
                this.episodeInfo.textContent = 'No videos found';
                return;
            }

            this.video.onended = () => {
                this.manualOverride = false;
                this.nextEpisode();
            };

            // Start from middle episode
            this.manualOverride = false;
            const live = this.getLivePosition();
            this.currentIndex = live.index;
            this.liveStartTime = live.time;
            this.playCurrentEpisode();
        } catch (error) {
            console.error('Error initializing channel player:', error);
        }
    }

    playCurrentEpisode() {
        if (this.episodes.length === 0) return;

        const episode = this.episodes[this.currentIndex];
        const video = this.video;

        video.pause();
        video.src = "/api/video/" + encodeURIComponent(episode.path);
        video.load();

        video.onloadedmetadata = () => {
            // "Live TV" feel: start in the middle
            const startTime = this.manualOverride
                ? 0
                : Math.min(this.liveStartTime || 0, video.duration - 1);

            video.currentTime = startTime;
            video.play();

            
            // ✅ auto fullscreen for Live TV
            setTimeout(() => {
                if (!document.fullscreenElement) {
                    document
                    .querySelector('#channel-player .player-container')
                    ?.requestFullscreen()
                    .catch(() => {});
                }
            }, 0);
            
            app.setSubtitle('he');
        };

        this.updateEpisodeInfo();
    }

    getLivePosition() {
        const totalEpisodes = this.episodes.length;
        if (totalEpisodes === 0) return { index: 0, time: 0 };

        // Total duration of one full loop (estimate: use metadata later if you want)
        const EST_EPISODE_LENGTH = 22 * 60; // 22 minutes (safe default)
        const loopDuration = totalEpisodes * EST_EPISODE_LENGTH;

        // Use real time as the clock
        const now = Math.floor(Date.now() / 1000);
        const positionInLoop = now % loopDuration;

        const episodeIndex = Math.floor(positionInLoop / EST_EPISODE_LENGTH);
        const timeInEpisode = positionInLoop % EST_EPISODE_LENGTH;

        return {
            index: episodeIndex,
            time: timeInEpisode
        };
    }



    updateEpisodeInfo() {
        const episode = this.episodes[this.currentIndex];
        const total = this.episodes.length;
        this.episodeInfo.textContent = `${episode.filename} (${this.currentIndex + 1}/${total})`;
    }

    nextEpisode() {
        this.manualOverride = true;
        this.currentIndex = (this.currentIndex + 1) % this.episodes.length;
        this.playCurrentEpisode();
    }

    previousEpisode() {
        this.manualOverride = true;
        this.currentIndex = (this.currentIndex - 1 + this.episodes.length) % this.episodes.length;
        this.playCurrentEpisode();
    }
}

function exitFullscreenIfNeeded() {
    if (document.fullscreenElement) {
        document.exitFullscreen().catch(() => {});
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    app.init();
});
