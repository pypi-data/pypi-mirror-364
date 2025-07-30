import setuptools
with open('README.md', 'r', encoding='utf-8') as fh:
	long_description = fh.read()

setuptools.setup(
	name='HdRezkaApi',
	version='11.1.0',
	author='Super_Zombi',
	author_email='super.zombi.yt@gmail.com',
	description='HDRezka Python API',
	long_description=long_description,
	long_description_content_type='text/markdown',
	url='https://github.com/SuperZombi/HdRezkaApi',
	project_urls={
		'Documentation': 'https://superzombi.github.io/HdRezkaApi/',
	},
	packages=['HdRezkaApi'],
	install_requires=["beautifulsoup4", "requests"],
	include_package_data=True,
	classifiers=[
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
	],
	python_requires='>=3.9',
)