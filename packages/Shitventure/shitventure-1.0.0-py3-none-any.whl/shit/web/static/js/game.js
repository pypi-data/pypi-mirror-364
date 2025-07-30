class ToiletDetectiveGame {
    constructor() {
        this.suspects = [];
        this.currentSuspect = null;
        this.clues = {
            footprints: false,
            fingerprints: false,
            dna: false
        };
        this.nauseaLevel = 0;
        
        this.initElements();
        this.loadGame();
        this.setupEventListeners();
    }
    
    initElements() {
        this.suspectsList = document.getElementById('suspects-list');
        this.footprintsBtn = document.getElementById('check-footprints');
        this.fingerprintsBtn = document.getElementById('check-fingerprints');
        this.dnaBtn = document.getElementById('check-dna');
        this.nauseaLevelDisplay = document.getElementById('nausea-level');
        this.nauseaFill = document.getElementById('nausea-fill');
    }
    
    async loadGame() {
        try {
            const response = await fetch('/api/game');
            const data = await response.json();
            
            this.suspects = data.suspects;
            this.renderSuspects();
            
            // 每5秒增加1点孕吐值
            this.nauseaInterval = setInterval(() => {
                this.increaseNausea(1);
            }, 5000);
            
        } catch (error) {
            console.error('加载游戏失败:', error);
            alert('游戏加载失败，请刷新页面重试');
        }
    }
    
    renderSuspects() {
        this.suspectsList.innerHTML = '';
        
        this.suspects.forEach(suspect => {
            const card = document.createElement('div');
            card.className = 'suspect-card';
            card.innerHTML = `
                <h4>${suspect.name}</h4>
                <p>${suspect.description}</p>
                <div class="suspect-level">可疑度: ${'★'.repeat(suspect.suspicious_level)}</div>
            `;
            
            card.addEventListener('click', () => {
                this.selectSuspect(suspect);
            });
            
            this.suspectsList.appendChild(card);
        });
    }
    
    selectSuspect(suspect) {
        // 移除之前选中的样式
        document.querySelectorAll('.suspect-card').forEach(card => {
            card.classList.remove('selected');
        });
        
        // 添加新选中的样式
        event.currentTarget.classList.add('selected');
        this.currentSuspect = suspect;
        
        // 检查线索
        this.checkClues();
    }
    
    checkClues() {
        if (!this.currentSuspect) return;
        
        this.clues = {
            footprints: this.currentSuspect.footprints,
            fingerprints: this.currentSuspect.fingerprints,
            dna: this.currentSuspect.dna
        };
        
        this.updateClueButtons();
    }
    
    updateClueButtons() {
        this.footprintsBtn.disabled = !this.clues.footprints;
        this.fingerprintsBtn.disabled = !this.clues.fingerprints;
        this.dnaBtn.disabled = !this.clues.dna;
    }
    
    increaseNausea(amount) {
        this.nauseaLevel = Math.min(this.nauseaLevel + amount, 10);
        this.nauseaLevelDisplay.textContent = this.nauseaLevel;
        this.nauseaFill.style.width = `${this.nauseaLevel * 10}%`;
        
        if (this.nauseaLevel >= 10) {
            this.gameOver();
        }
    }
    
    gameOver() {
        clearInterval(this.nauseaInterval);
        alert('孕吐太厉害，游戏结束！');
    }
    
    setupEventListeners() {
        this.footprintsBtn.addEventListener('click', () => {
            this.increaseNausea(1);
            this.showClueResult('footprints', '发现了匹配的足迹！');
        });
        
        this.fingerprintsBtn.addEventListener('click', () => {
            this.increaseNausea(1);
            this.showClueResult('fingerprints', '发现了匹配的指纹！');
        });
        
        this.dnaBtn.addEventListener('click', () => {
            this.increaseNausea(1);
            this.showClueResult('dna', '发现了匹配的DNA！');
        });

        // 确认按钮事件
        this.confirmBtn = document.getElementById('confirm-btn');
        this.confirmBtn.addEventListener('click', () => {
            this.confirmSelection();
        });

        // 结果区域
        this.resultArea = document.getElementById('result-area');
    }

    showClueResult(clueType, message) {
        if (this.currentSuspect && this.currentSuspect[clueType]) {
            this.resultArea.textContent = message;
            this.resultArea.style.color = '#28a745';
        } else {
            this.resultArea.textContent = '没有发现匹配的线索';
            this.resultArea.style.color = '#dc3545';
        }
    }

    selectSuspect(suspect) {
        // 移除之前选中的样式
        document.querySelectorAll('.suspect-card').forEach(card => {
            card.classList.remove('selected');
        });
        
        // 添加新选中的样式
        event.currentTarget.classList.add('selected');
        this.currentSuspect = suspect;
        this.confirmBtn.disabled = false;
        
        // 检查线索
        this.checkClues();
        this.resultArea.textContent = `已选择: ${suspect.name}`;
        this.resultArea.style.color = '#17a2b8';
    }

    confirmSelection() {
        if (!this.currentSuspect) return;

        // 检查是否是真正的拉屎者
        const isCulprit = this.currentSuspect.footprints && 
                         this.currentSuspect.fingerprints && 
                         this.currentSuspect.dna;
        
        if (isCulprit) {
            this.resultArea.textContent = `正确！${this.currentSuspect.name}就是拉屎的人！`;
            this.resultArea.style.color = '#28a745';
            clearInterval(this.nauseaInterval);
        } else {
            this.increaseNausea(2); // 错误选择惩罚
            this.resultArea.textContent = `错误！${this.currentSuspect.name}不是拉屎的人！`;
            this.resultArea.style.color = '#dc3545';
        }

        this.confirmBtn.disabled = true;
    }
}

// 初始化游戏
document.addEventListener('DOMContentLoaded', () => {
    new ToiletDetectiveGame();
});
