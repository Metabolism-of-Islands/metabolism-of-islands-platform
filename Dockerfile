# Use the official Python image
FROM python:3.8

# Install system dependencies for GDAL
RUN apt-get update -y && apt-get install --no-install-recommends -y \
    software-properties-common \
    gdal-bin libgdal-dev \
    binutils libproj-dev ffmpeg gettext locales

# Verify GDAL installation
RUN gdalinfo --version

# Set environment variables for GDAL inside the container
ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal
ENV GDAL_CONFIG=/usr/bin/gdal-config

# Set Python environment
ENV PYTHONUNBUFFERED 1

# Create necessary directories
RUN mkdir /src /static
WORKDIR /src

# Copy the application source code
ADD ./src /src

# Upgrade pip and install dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.pip
