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
        // Stop any playing videos when switching views
        document.querySelectorAll('video').forEach(v => {
            v.pause();
            v.removeAttribute('src');
            v.load();
        });

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

    async goToVOD() {
        this.showView('vod-view');
        await this.loadSeasons();
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
    async loadSeasons() {
        try {
            const response = await fetch(`${this.apiUrl}/seasons`);
            const seasons = await response.json();
            this.renderSeasons(seasons);
        } catch (error) {
            console.error('Error loading seasons:', error);
        }
    },

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

        // Remove old tracks
        [...video.querySelectorAll('track')].forEach(t => t.remove());

        if (!lang) {
            video.load();
            return;
        }

        // 🔑 IMPORTANT: decode the video API path back to filesystem path
        const videoApiSrc = video.currentSrc;
        if (!videoApiSrc.includes('/api/video/')) return;

        const encodedPath = videoApiSrc.split('/api/video/')[1];
        const filePath = decodeURIComponent(encodedPath);

        // Strip extension
        const basePath = filePath.replace(/\.(mp4|mkv|webm)$/i, '');

        let subtitlePath;
        if (lang === 'he') {
            subtitlePath = `${basePath}.vtt`;
        } else if (lang === 'en') {
            subtitlePath = `${basePath}.en.vtt`;
        }

        // 🔑 Route subtitles THROUGH THE API
        const subtitleApiUrl = `/api/video/${encodeURIComponent(subtitlePath)}`;

        const track = document.createElement('track');
        track.kind = 'subtitles';
        track.label = lang.toUpperCase();
        track.srclang = lang;
        track.src = subtitleApiUrl;
        track.default = true;

        video.appendChild(track);

        video.load(); // forces browser to fetch subtitle
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
            card.onclick = () => this.playVODEpisode(episode);
            container.appendChild(card);
        });
    },

    async playVODEpisode(episode) {
        this.showView('vod-player');
        const video = document.getElementById('vod-video');
        const videoPath = episode.path.replace(/\\/g, '__SLASH__');
        video.src = `${this.apiUrl}/video/${videoPath}`;
    },

    // Event Listeners
    attachEventListeners() {
        let uiTimeout;
        let liveTimeout;

        document.addEventListener('mousemove', () => {
            const playerUI = document.querySelector('.player-ui');
            const liveIndicator = document.getElementById('live-indicator');

            // Show player UI (existing behavior)
            if (playerUI && !playerUI.classList.contains('vod-ui')) {
                playerUI.classList.add('visible');
                clearTimeout(uiTimeout);
                uiTimeout = setTimeout(() => {
                    playerUI.classList.remove('visible');
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
                this.initialize(); // re-ask “what’s live now”
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

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    app.init();
});
