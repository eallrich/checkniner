#!/bin/bash

ls | grep .tar.gz | grep -v latest | xargs rm
