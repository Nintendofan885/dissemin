# Dissemin: open access policy enforcement tool
# Copyright (C) 2014 Antonin Delpeuch
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Affero General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#

import os

from publishers.tests.test_romeo import RomeoAPIStub
from papers.models import Paper
from papers.tests.test_pages import RenderingTest


class JournalPageTest(RenderingTest):
    @classmethod
    def setUpClass(cls):
        super(JournalPageTest, cls).setUpClass()
        cls.testdir = os.path.dirname(os.path.abspath(__file__))
        cls.api = RomeoAPIStub(os.path.join(cls.testdir, 'data'))

    def test_escaping(self):
        # issue #115
        # in the meantime the journal has been deleted from sherpa
        journal = self.api.fetch_journal({'issn': '0302-9743'})
        # Small hack to make the journal appear in the publisher's journal list
        journal.update_stats()
        journal.stats.num_tot = 1
        journal.stats.save()
        publisher = journal.publisher
        r = self.getPage('publisher', kwargs={
                         'pk': publisher.pk, 'slug': publisher.slug})
        self.checkHtml(r)

    def test_publisher_url(self):
        p = Paper.create_by_doi('10.1007/978-3-642-14363-2_7')
        for publi in p.publications:
            self.checkPage('publisher', kwargs={
                           'pk': publi.publisher_id, 'slug': publi.publisher.slug})
