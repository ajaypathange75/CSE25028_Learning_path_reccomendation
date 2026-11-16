// ==========================================================================
// AI Career Path - Interactive Client Utilities
// Provides rich micro-interactions, tab switching, wizard progression,
// filtering, code copy, and accessibility enhancements across all pages.
// ==========================================================================

document.addEventListener("DOMContentLoaded", () => {
  // 0. Dynamic Navbar Active Tab Highlighting based on Current URL
  function syncActiveNavbarTab() {
    const path = window.location.pathname;
    const navLinks = document.querySelectorAll(".nav-link");
    navLinks.forEach(link => link.classList.remove("active"));

    if (path.startsWith("/dashboard")) {
      document.getElementById("nav-dashboard")?.classList.add("active");
    } else if (path.startsWith("/career")) {
      document.getElementById("nav-assessment")?.classList.add("active");
    } else if (path.startsWith("/learning/projects")) {
      document.getElementById("nav-projects")?.classList.add("active");
    } else if (path.startsWith("/learning/roadmap") || path.startsWith("/learning/concept") || path.startsWith("/learning/activity")) {
      document.getElementById("nav-roadmap")?.classList.add("active");
    } else if (path.startsWith("/assessment")) {
      document.getElementById("nav-history")?.classList.add("active");
    } else if (path.startsWith("/profile")) {
      document.getElementById("nav-profile")?.classList.add("active");
    } else if (path.startsWith("/login")) {
      document.getElementById("nav-login")?.classList.add("active");
    }
  }
  syncActiveNavbarTab();

  // 1. Generic Tab Switcher
  const tabContainers = document.querySelectorAll("[data-tabs-group]");
  tabContainers.forEach(group => {
    const tabs = group.querySelectorAll(".nav-tab-item");
    const contents = group.querySelectorAll(".tab-pane");

    tabs.forEach(tab => {
      tab.addEventListener("click", (e) => {
        e.preventDefault();
        const targetId = tab.getAttribute("data-tab-target");

        tabs.forEach(t => t.classList.remove("active"));
        contents.forEach(c => c.style.display = "none");

        tab.classList.add("active");
        const activeContent = document.getElementById(targetId);
        if (activeContent) {
          activeContent.style.display = "block";
        }
      });
    });
  });

  // 2. Interactive Step Wizard (for Career Assessment & Onboarding)
  const wizard = document.getElementById("career-assessment-wizard");
  if (wizard) {
    const steps = wizard.querySelectorAll(".wizard-step");
    const stepCards = wizard.querySelectorAll(".wizard-step-card");
    const btnNextList = wizard.querySelectorAll(".wizard-btn-next");
    const btnPrevList = wizard.querySelectorAll(".wizard-btn-prev");
    let currentStep = 0;

    function showStep(index) {
      if (index < 0 || index >= stepCards.length) return;
      currentStep = index;

      stepCards.forEach((card, idx) => {
        card.style.display = idx === index ? "block" : "none";
      });

      steps.forEach((step, idx) => {
        step.classList.remove("active", "completed");
        if (idx === index) {
          step.classList.add("active");
        } else if (idx < index) {
          step.classList.add("completed");
        }
      });

      // Smooth scroll to top of wizard
      wizard.scrollIntoView({ behavior: "smooth", block: "start" });
    }

    steps.forEach((step, idx) => {
      step.addEventListener("click", () => {
        showStep(idx);
      });
    });

    btnNextList.forEach(btn => {
      btn.addEventListener("click", () => {
        showStep(currentStep + 1);
      });
    });

    btnPrevList.forEach(btn => {
      btn.addEventListener("click", () => {
        showStep(currentStep - 1);
      });
    });

    // Initialize first step
    showStep(0);
  }

  // 3. Filter Pills Logic (e.g. Filter by Mastered, Developing, Weak, or Stage)
  const filterContainers = document.querySelectorAll("[data-filter-group]");
  filterContainers.forEach(container => {
    const pills = container.querySelectorAll(".filter-pill");
    const targetItems = document.querySelectorAll(container.getAttribute("data-filter-target"));

    pills.forEach(pill => {
      pill.addEventListener("click", (e) => {
        e.preventDefault();
        const filterVal = pill.getAttribute("data-filter-value");

        pills.forEach(p => p.classList.remove("active"));
        pill.classList.add("active");

        targetItems.forEach(item => {
          const itemVal = item.getAttribute("data-category") || "";
          if (filterVal === "all" || itemVal.toLowerCase().includes(filterVal.toLowerCase())) {
            item.style.display = "";
          } else {
            item.style.display = "none";
          }
        });
      });
    });
  });

  // 4. Real-time Search Filter for Tables & Card Lists
  const searchInputs = document.querySelectorAll("[data-search-target]");
  searchInputs.forEach(input => {
    const targetSelector = input.getAttribute("data-search-target");
    const items = document.querySelectorAll(targetSelector);

    input.addEventListener("input", (e) => {
      const term = e.target.value.toLowerCase().trim();
      items.forEach(item => {
        const text = item.textContent.toLowerCase();
        if (!term || text.includes(term)) {
          item.style.display = "";
        } else {
          item.style.display = "none";
        }
      });
    });
  });

  // 5. Expand / Collapse Accordion
  const accordionHeaders = document.querySelectorAll(".accordion-header");
  accordionHeaders.forEach(header => {
    header.addEventListener("click", () => {
      const parent = header.parentElement;
      const content = parent.querySelector(".accordion-content");
      const icon = header.querySelector(".accordion-icon");

      if (content.style.display === "none" || !content.style.display) {
        content.style.display = "block";
        if (icon) icon.textContent = "−";
      } else {
        content.style.display = "none";
        if (icon) icon.textContent = "+";
      }
    });
  });

  // 6. Interactive Code Snippet Copy Button
  const codeBlocks = document.querySelectorAll(".code-block");
  codeBlocks.forEach(block => {
    if (!block.querySelector(".code-copy-btn")) {
      const btn = document.createElement("button");
      btn.className = "code-copy-btn";
      btn.type = "button";
      btn.textContent = "Copy";
      block.appendChild(btn);

      btn.addEventListener("click", () => {
        const codeText = block.querySelector("code") ? block.querySelector("code").innerText : block.innerText;
        navigator.clipboard.writeText(codeText.replace("Copy", "").trim()).then(() => {
          btn.textContent = "Copied!";
          setTimeout(() => {
            btn.textContent = "Copy";
          }, 2000);
        });
      });
    }
  });

  // 7. Password Visibility Toggle
  const togglePassBtns = document.querySelectorAll(".toggle-password-btn");
  togglePassBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      const targetId = btn.getAttribute("data-target-input");
      const input = document.getElementById(targetId);
      if (input) {
        if (input.type === "password") {
          input.type = "text";
          btn.textContent = "Hide";
        } else {
          input.type = "password";
          btn.textContent = "Show";
        }
      }
    });
  });

  // 8. Form submit feedback & double-click prevention
  const forms = document.querySelectorAll("form");
  forms.forEach(form => {
    form.addEventListener("submit", () => {
      const submitBtn = form.querySelector("button[type='submit']");
      if (submitBtn && !submitBtn.disabled) {
        submitBtn.dataset.originalText = submitBtn.innerHTML;
        submitBtn.innerHTML = `
          <svg style="animation: spin 1s linear infinite; display: inline-block; vertical-align: middle; margin-right: 6px;" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10" stroke-opacity="0.25"></circle>
            <path d="M12 2a10 10 0 0 1 10 10"></path>
          </svg>
          Processing...
        `;
        submitBtn.disabled = true;
        // Re-enable after 12s safeguard
        setTimeout(() => {
          submitBtn.disabled = false;
          submitBtn.innerHTML = submitBtn.dataset.originalText || "Submit";
        }, 12000);
      }
    });
  });

  // 9. Interactive Roadmap Modules: Checkboxes, Drawer Expander, Copy, Prerequisite Search, Tier Toggles
  const roadmapStages = document.querySelectorAll(".roadmap-stage-card");
  if (roadmapStages.length > 0) {
    // 9a. Progress & Checkbox State
    function updateTierProgress(tierNum) {
      const stageCard = document.getElementById(`stage-card-${tierNum}`);
      if (!stageCard) return;

      const checks = stageCard.querySelectorAll(".module-study-check");
      const total = checks.length;
      let completed = 0;

      checks.forEach(chk => {
        if (chk.checked) completed++;
      });

      const counter = stageCard.querySelector(".stage-completed-counter");
      if (counter) {
        counter.textContent = `${completed} / ${total} Studied`;
      }

      const fill = document.getElementById(`stage-fill-${tierNum}`);
      if (fill) {
        const pct = total > 0 ? Math.round((completed / total) * 100) : 0;
        fill.style.width = `${pct}%`;
      }
    }

    const studyCheckboxes = document.querySelectorAll(".module-study-check");
    studyCheckboxes.forEach(chk => {
      const cid = chk.dataset.conceptId;
      const tier = chk.dataset.tier;
      if (cid) {
        const isChecked = localStorage.getItem(`roadmap_studied_${cid}`) === "true";
        if (isChecked) {
          chk.checked = true;
          chk.closest(".roadmap-module-item")?.classList.add("is-completed");
        }
      }

      chk.addEventListener("change", () => {
        if (cid) {
          localStorage.setItem(`roadmap_studied_${cid}`, chk.checked ? "true" : "false");
        }
        chk.closest(".roadmap-module-item")?.classList.toggle("is-completed", chk.checked);
        updateTierProgress(tier);
      });
    });

    // Initialize progress bars for all stages
    roadmapStages.forEach((_, idx) => updateTierProgress(idx + 1));

    // 9b. Module Details Drawer Expander
    const drawerButtons = document.querySelectorAll(".btn-toggle-module-details");
    drawerButtons.forEach(btn => {
      btn.addEventListener("click", (e) => {
        e.preventDefault();
        const drawerId = btn.getAttribute("data-drawer-target");
        const drawer = document.getElementById(drawerId);
        if (drawer) {
          const isOpen = drawer.classList.contains("open");
          if (isOpen) {
            drawer.classList.remove("open");
            btn.classList.remove("expanded");
          } else {
            drawer.classList.add("open");
            btn.classList.add("expanded");
          }
        }
      });
    });

    // 9c. Copy Concept Title
    const copyBtns = document.querySelectorAll(".btn-copy-concept");
    copyBtns.forEach(btn => {
      btn.addEventListener("click", (e) => {
        e.preventDefault();
        const textToCopy = btn.getAttribute("data-copy");
        if (textToCopy) {
          navigator.clipboard.writeText(textToCopy).then(() => {
            const originalHTML = btn.innerHTML;
            btn.innerHTML = `<svg class="icon icon-sm" viewBox="0 0 24 24" style="stroke: var(--success);"><polyline points="20 6 9 17 4 12"/></svg>`;
            setTimeout(() => {
              btn.innerHTML = originalHTML;
            }, 1800);
          });
        }
      });
    });

    // 9d. Clickable Prerequisite Pill to Search & Jump
    const prereqPills = document.querySelectorAll(".prereq-clickable-pill");
    const searchInput = document.getElementById("roadmap-search-input");
    prereqPills.forEach(pill => {
      pill.addEventListener("click", () => {
        const term = pill.getAttribute("data-prereq-search");
        if (term && searchInput) {
          searchInput.value = term;
          searchInput.dispatchEvent(new Event("input"));
          searchInput.scrollIntoView({ behavior: "smooth", block: "center" });
        }
      });
    });

    // 9e. Individual Stage Accordion Toggle
    const stageHeaders = document.querySelectorAll("[data-toggle-stage]");
    stageHeaders.forEach(hdr => {
      hdr.addEventListener("click", () => {
        const targetBodyId = hdr.getAttribute("data-toggle-stage");
        const body = document.getElementById(targetBodyId);
        const toggleBtn = hdr.querySelector(".stage-toggle-btn");
        if (body) {
          const isHidden = body.style.display === "none";
          body.style.display = isHidden ? "block" : "none";
          toggleBtn?.classList.toggle("collapsed", !isHidden);
        }
      });
    });

    // 9f. Expand All / Collapse All Tiers
    const toggleAllBtn = document.getElementById("btn-toggle-all-tiers");
    const toggleAllText = document.getElementById("toggle-all-tiers-text");
    let allExpanded = true;
    if (toggleAllBtn) {
      toggleAllBtn.addEventListener("click", () => {
        allExpanded = !allExpanded;
        roadmapStages.forEach((stage, idx) => {
          const tierNum = idx + 1;
          const body = document.getElementById(`stage-body-${tierNum}`);
          const toggleBtn = document.getElementById(`stage-toggle-btn-${tierNum}`);
          if (body) {
            body.style.display = allExpanded ? "block" : "none";
          }
          toggleBtn?.classList.toggle("collapsed", !allExpanded);
        });
        if (toggleAllText) {
          toggleAllText.textContent = allExpanded ? "Collapse Tiers" : "Expand Tiers";
        }
      });
    }
  }

  // 10. Interactive Concept Action Dock (Study Status & Quiz Launch Deck)
  const statusSelect = document.getElementById("activity-status-select");
  const statusDot = document.getElementById("status-live-dot");
  if (statusSelect && statusDot) {
    statusSelect.addEventListener("change", (e) => {
      const val = e.target.value;
      statusDot.className = "status-live-dot";
      if (val === "completed") {
        statusDot.classList.add("dot-completed");
      } else if (val === "in_progress") {
        statusDot.classList.add("dot-in_progress");
      } else {
        statusDot.classList.add("dot-pending");
      }
    });
  }

  const statusForm = document.getElementById("activity-update-form");
  if (statusForm) {
    statusForm.addEventListener("submit", () => {
      const btn = document.getElementById("update-status-submit-btn");
      const textSpan = document.getElementById("update-status-btn-text");
      const icon = btn?.querySelector(".sync-icon");
      if (btn && textSpan) {
        textSpan.textContent = "Updating...";
        if (icon) {
          icon.style.animation = "spin 0.8s linear infinite";
        }
      }
    });
  }

  // Interactive Live Quiz Hints on Hover
  const quizPillBtns = document.querySelectorAll(".quiz-pill-btn");
  const quizHintText = document.getElementById("quiz-hint-live-text");
  const defaultHint = "Select a practice length to evaluate your Bayesian Knowledge Tracing (BKT) score.";
  
  quizPillBtns.forEach(btn => {
    btn.addEventListener("mouseenter", () => {
      const hint = btn.getAttribute("data-hint");
      if (hint && quizHintText) {
        quizHintText.textContent = hint;
        quizHintText.style.color = "var(--text-main)";
        quizHintText.style.fontWeight = "600";
      }
    });

    btn.addEventListener("mouseleave", () => {
      if (quizHintText) {
        quizHintText.textContent = defaultHint;
        quizHintText.style.color = "var(--text-muted)";
        quizHintText.style.fontWeight = "normal";
      }
    });
  });

  // 11. Interactive Code Studio Tabs (Production Code, Walkthrough, Terminal, SOLID, Pitfalls)
  const studioTabs = document.querySelectorAll(".code-studio-tab");
  studioTabs.forEach(tab => {
    tab.addEventListener("click", () => {
      const targetPaneId = tab.getAttribute("data-code-target");
      if (!targetPaneId) return;

      studioTabs.forEach(t => t.classList.remove("active"));
      tab.classList.add("active");

      const panes = document.querySelectorAll(".code-tab-pane");
      panes.forEach(pane => {
        pane.classList.remove("active");
        if (pane.id === targetPaneId) {
          pane.classList.add("active");
        }
      });
    });
  });

  // 12. One-Click Copy Code Button with Instant Visual Feedback
  const copyCodeBtn = document.getElementById("copy-code-lab-btn");
  if (copyCodeBtn) {
    copyCodeBtn.addEventListener("click", async () => {
      const codeSnippet = document.getElementById("code-snippet-pre");
      if (!codeSnippet) return;

      const textToCopy = codeSnippet.innerText || codeSnippet.textContent;
      try {
        await navigator.clipboard.writeText(textToCopy);
        const originalHtml = copyCodeBtn.innerHTML;
        copyCodeBtn.innerHTML = `
          <svg class="icon icon-sm" viewBox="0 0 24 24" style="stroke: #10b981;"><polyline points="20 6 9 17 4 12"></polyline></svg>
          <span style="color: #10b981; font-weight: 800;">Copied!</span>
        `;
        copyCodeBtn.style.borderColor = "#10b981";
        setTimeout(() => {
          copyCodeBtn.innerHTML = originalHtml;
          copyCodeBtn.style.borderColor = "";
        }, 2200);
      } catch (err) {
        console.error("Failed to copy code snippet: ", err);
      }
    });
  }

  // 13. Interactive Code Challenge Accordion
  const challengeTriggers = document.querySelectorAll(".challenge-trigger");
  challengeTriggers.forEach(trigger => {
    trigger.addEventListener("click", () => {
      const parentItem = trigger.closest(".challenge-item");
      if (parentItem) {
        parentItem.classList.toggle("open");
      }
    });
  });
});

