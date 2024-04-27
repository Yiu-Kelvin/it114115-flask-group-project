#!/bin/sh
flask db upgrade
flask --debug run --host=0.0.0.0