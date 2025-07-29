from setuptools import setup, find_packages

# Read long description and dependencies
with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

with open("requirements.txt", encoding="utf-8") as f:
    requirements = f.read().splitlines()

# =====================================================================
#                           AUTHORS SECTION
# =====================================================================
# 🎓 PRIMARY AUTHOR & PRINCIPAL INVESTIGATOR:
#   Dr. H.S. Nagendraswamy
#   Professor, Department of Studies in Computer Science
#   University of Mysore, Karnataka, India
#   Expertise: Pattern Recognition, Image Processing, Data Mining,
#             Fuzzy Theory, Symbolic Data Analysis
#   Email: hsnagendraswamy@gmail.com
#   Profile: https://uni-mysore.ac.in/english-version/content.php?id=246
#
# 👥 CO-AUTHORS & RESEARCH CONTRIBUTORS:
#   Maheshwari N - Research Contributor & Developer
#   LinkedIn: https://www.linkedin.com/in/maheshwari-maheshwari-692770341/
#
#   Somanna M - Lead Developer & Technical Contributor
#   LinkedIn: https://www.linkedin.com/in/somanna-m
#   Email: somudotm@gmail.com
# =====================================================================

setup(
    name="deeplabelnet",
    version="0.1.15",
    packages=find_packages(),
    include_package_data=True,
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "deeplabelnet = deeplabelnet_launcher.__main__:main"
        ],
    },

    # =====================================================================
    #                    🎯 AUTHORS (PRIMARY FOCUS)
    # =====================================================================
    author="Dr H.S. Nagendraswamy, Maheshwari N, Somanna M",
    author_email="hsnagendraswamy@gmail.com",
    # =====================================================================

    # =====================================================================
    #                      🔧 MAINTAINER INFO
    # =====================================================================
    maintainer="Somanna M",
    maintainer_email="somudotm@gmail.com",
    # =====================================================================

    description="DeepLabelNet: Advanced Jupyter-like image annotation tool for Computer Vision Tasks",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://bitbucket.org/your-bitbucket-username/deeplabelnet",

    # =====================================================================
    #                    🔗 AUTHOR PROFILES & LINKS
    # =====================================================================
    project_urls={
        # 🎓 Primary Author - Academic Profile
        "👨‍🎓 Dr H.S. Nagendraswamy ": "https://uni-mysore.ac.in/english-version/content.php?id=246",

        # 👥 Co-Authors - Professional Profiles
        "💼 Maheshwari N ": "https://www.linkedin.com/in/maheshwari-maheshwari-692770341/",
        "💼 Somanna M ": "https://www.linkedin.com/in/somanna-m",

        # 🏛️ Institution
        "🏛️ UoM -DoS in CS": "https://uni-mysore.ac.in/",


    },
    # =====================================================================

    keywords=[

        # Tool & Technology Keywords
        "Image annotation", "Django", "Jupyter", "Deep learning",
        "Machine learning", "Research tool", "Academic software",
    ],

    classifiers=[
        "Development Status :: 4 - Beta",
        "Framework :: Django",
        "Framework :: Django :: 3.0",
        "Framework :: Django :: 4.0",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",

        # 🎯 AUDIENCE (Highlighting Academic/Research Focus)
        "Intended Audience :: Science/Research",
        "Intended Audience :: Education",
        "Intended Audience :: Developers",

        # 🔬 RESEARCH TOPICS (Highlighting Dr. Nagendraswamy's Areas)
        "Topic :: Scientific/Engineering :: Image Recognition",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Education :: Computer Aided Instruction (CAI)",
        "Topic :: Software Development :: Build Tools",
        "Topic :: Multimedia :: Graphics :: Graphics Conversion",
        "Environment :: Web Environment",
    ],

    python_requires=">=3.8",
    license="GPL-3.0",
    zip_safe=False,
)
